"""Live segmentation demos. Usage: uv run live_demo/segment.py {classical|deep|face|compare} [--camera N] | --selftest"""
import argparse
import sys
import threading
import time
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import cv2
import mediapipe as mp
import numpy as np
import onnxruntime as ort
from mediapipe.tasks.python import BaseOptions, vision

MODELS = Path(__file__).parent / "models"
URLS = {
    "selfie_multiclass_256x256.tflite": "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite",
    "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
    # BiSeNet trained on CelebAMask-HQ (19 face classes), MIT licence: github.com/yakhyo/face-parsing
    "bisenet_resnet34.onnx": "https://github.com/yakhyo/face-parsing/releases/download/v0.0.2/resnet34.onnx",
}


def hex_bgr(h):
    return tuple(int(h[i:i + 2], 16) for i in (5, 3, 1))


CYAN, RUST, LIGHT = hex_bgr("#2BB8C4"), hex_bgr("#D9481F"), (240, 240, 240)

# MediaPipe selfie multiclass labels, same colours as the slides.
BODY = [("tlo", "#2A2D34"), ("wlosy", "#7A3B5E"), ("skora ciala", "#E0B98A"),
        ("skora twarzy", "#D9A066"), ("ubranie", "#6E7F5B"), ("inne", "#E8C547")]
BODY_PALETTE = np.array([hex_bgr(c) for _, c in BODY], dtype=np.uint8)

# CelebAMask-HQ class ids (BiSeNet order) grouped for display.
FACE_GROUPS = [
    ("skora", "#D9A066", [1, 7, 8, 10, 14]),
    ("brwi", "#5B3A29", [2, 3]),
    ("oczy", "#E8C547", [4, 5]),
    ("okulary", "#2BB8C4", [6]),
    ("usta", "#D9481F", [11, 12, 13]),
    ("wlosy", "#7A3B5E", [17]),
    ("ubranie", "#6E7F5B", [16]),
    ("kapelusz", "#3D5A80", [18]),
    ("bizuteria", "#B76E79", [9, 15]),
]
GLASSES = 6
FACE_PALETTE = np.zeros((19, 3), np.uint8)
for _, color, ids in FACE_GROUPS:
    FACE_PALETTE[ids] = hex_bgr(color)

MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)


def model_path(name):
    path = MODELS / name
    if not path.exists():
        MODELS.mkdir(exist_ok=True)
        print(f"Pobieram {name}...")
        urllib.request.urlretrieve(URLS[name], path)
    return str(path)


def legend(img, items):
    for i, (name, color) in enumerate(items):
        y = 30 + i * 28
        cv2.rectangle(img, (10, y - 18), (32, y + 4), color, -1)
        cv2.rectangle(img, (10, y - 18), (32, y + 4), LIGHT, 1)
        cv2.putText(img, name, (40, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, LIGHT, 1, cv2.LINE_AA)


# --- 1. classical -------------------------------------------------------------------------------

def classical(frame):
    """Skin-colour threshold in YCrCb, refined by GrabCut on a downscaled frame."""
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    skin = cv2.inRange(ycrcb, (0, 133, 77), (255, 173, 127))
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    small = cv2.resize(frame, None, fx=0.25, fy=0.25)
    small_skin = cv2.resize(skin, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    if 50 < cv2.countNonZero(small_skin) < small_skin.size - 50:  # GrabCut needs both fg and bg samples
        gc = np.where(small_skin > 0, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
        bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        cv2.grabCut(small, gc, None, bgd, fgd, 1, cv2.GC_INIT_WITH_MASK)
        small_skin = np.where((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        skin = cv2.resize(small_skin, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST)

    out = (frame * 0.35).astype(np.uint8)
    out[skin > 0] = (0.5 * frame[skin > 0] + 0.5 * np.array(RUST)).astype(np.uint8)
    return out


# --- 2. MediaPipe multiclass body segmentation --------------------------------------------------

def body_mask(frame, segmenter):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mask = segmenter.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)).category_mask.numpy_view()
    return mask.reshape(mask.shape[:2]).copy()


def deep(frame, mask):
    if mask is None:
        return frame.copy()
    mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST)
    out = cv2.addWeighted(frame, 0.35, BODY_PALETTE[mask], 0.65, 0)
    legend(out, [(n, hex_bgr(c)) for n, c in BODY])
    return out


# --- 3. face parsing: detect face, crop, BiSeNet 19 classes ------------------------------------

def face_box(landmarks, w, h):
    """Square crop around the face with room for hair, like the aligned CelebA-HQ training images."""
    pts = np.array([(p.x * w, p.y * h) for p in landmarks])
    (x0, y0), (x1, y1) = pts.min(0), pts.max(0)
    side = int(1.9 * max(x1 - x0, y1 - y0))
    cx, cy = int((x0 + x1) / 2), int((y0 + y1) / 2 - 0.08 * side)
    return cx - side // 2, cy - side // 2, side


def bisenet():
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 4  # measured fastest on 8 cores; leaves room for the other network
    return ort.InferenceSession(model_path("bisenet_resnet34.onnx"), opts, providers=["CPUExecutionProvider"])


def parse(img, session):
    x = cv2.cvtColor(cv2.resize(img, (512, 512)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    x = ((x - MEAN) / STD).transpose(2, 0, 1)[None]
    labels = session.run(["output"], {session.get_inputs()[0].name: x})[0][0].argmax(0).astype(np.uint8)
    return cv2.resize(labels, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)


def face_mask(frame, landmarker, session):
    """Full-frame CelebAMask-HQ label map; 0 outside detected faces."""
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)).face_landmarks
    out = np.zeros((h, w), np.uint8)
    for face in faces:
        x, y, side = face_box(face, w, h)
        padded = cv2.copyMakeBorder(frame, side, side, side, side, cv2.BORDER_REPLICATE)
        labels = parse(padded[y + side:y + 2 * side, x + side:x + 2 * side], session)
        # paste back, clipping to the frame
        fx0, fy0, fx1, fy1 = max(x, 0), max(y, 0), min(x + side, w), min(y + side, h)
        crop = labels[fy0 - y:fy1 - y, fx0 - x:fx1 - x]
        region = out[fy0:fy1, fx0:fx1]
        region[crop > 0] = crop[crop > 0]
    return out


def face(frame, mask):
    out = (frame * 0.5).astype(np.uint8)
    if mask is None:
        return out
    parts = mask > 0
    out[parts] = (0.4 * frame[parts] + 0.6 * FACE_PALETTE[mask[parts]]).astype(np.uint8)
    glasses = (mask == GLASSES).astype(np.uint8)
    contours, _ = cv2.findContours(glasses, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(out, contours, -1, CYAN, 2, cv2.LINE_AA)

    present = set(np.unique(mask).tolist())
    legend(out, [(n, hex_bgr(c)) for n, c, ids in FACE_GROUPS if present & set(ids)])
    skin = max(int((mask == 1).sum()), 1)
    found = glasses.sum() / skin > 0.02  # ratio, so it works at any distance from the camera
    text, color = ("OKULARY WYKRYTE", CYAN) if found else ("brak okularow", LIGHT)
    if parts.any():
        cv2.putText(out, text, (out.shape[1] - 330, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)
    else:
        cv2.putText(out, "brak twarzy", (out.shape[1] - 200, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, RUST, 2, cv2.LINE_AA)
    return out


# --- live loop ----------------------------------------------------------------------------------

class Background:
    """Runs fn on the newest frame in a worker thread so the video stays smooth; .result lags slightly."""

    def __init__(self, fn):
        self.fn, self.frame, self.result, self.hz = fn, None, None, 0.0
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while True:
            frame, self.frame = self.frame, None
            if frame is None:
                time.sleep(0.005)
                continue
            t = time.perf_counter()
            self.result = self.fn(frame)
            self.hz = 1 / max(time.perf_counter() - t, 1e-6)


def label(img, text, fps):
    cv2.putText(img, f"{text}  {fps:4.1f} kl/s", (10, img.shape[0] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, LIGHT, 2, cv2.LINE_AA)
    return img


def run(mode, camera):
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        sys.exit(f"Nie mogę otworzyć kamery {camera}")

    panels = {"classical": ["classical"], "deep": ["deep"], "face": ["face"]}.get(mode, ["classical", "deep", "face"])
    workers = {}
    if "deep" in panels:
        seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
            base_options=BaseOptions(model_asset_path=model_path("selfie_multiclass_256x256.tflite")),
            output_category_mask=True))
        workers["deep"] = Background(lambda f: body_mask(f, seg))
    if "face" in panels:
        lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path("face_landmarker.task")), num_faces=2))
        net = bisenet()
        workers["face"] = Background(lambda f: face_mask(f, lmk, net))
    names = {"classical": "Klasyczna", "deep": "Siec wieloklasowa", "face": "Face parsing (19 klas)"}

    window = f"Segmentacja - {mode} (q = wyjscie)"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        imgs = []
        for p in panels:
            if p == "classical":
                t = time.perf_counter()
                img = classical(frame)
                fps = 1 / max(time.perf_counter() - t, 1e-6)
            else:
                workers[p].frame = frame
                img = (deep if p == "deep" else face)(frame, workers[p].result)
                fps = workers[p].hz
            imgs.append(label(img, names[p], fps))
        cv2.imshow(window, np.hstack(imgs))
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27) or cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
            break
    cap.release()
    cv2.destroyAllWindows()


def selftest():
    assert hex_bgr("#2BB8C4") == (0xC4, 0xB8, 0x2B)
    assert (FACE_PALETTE[GLASSES] == CYAN).all() and (FACE_PALETTE[0] == 0).all()
    frame = np.full((240, 320, 3), 40, np.uint8)
    cv2.ellipse(frame, (160, 120), (60, 80), 0, 0, 360, (120, 150, 210), -1)  # skin-ish blob

    out = classical(frame)
    assert out.shape == frame.shape and (out[120, 160] != out[10, 10]).any(), "skin blob should be highlighted"

    with vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
            base_options=BaseOptions(model_asset_path=model_path("selfie_multiclass_256x256.tflite")),
            output_category_mask=True)) as seg:
        mask = body_mask(frame, seg)
        assert mask.shape == frame.shape[:2]
        assert deep(frame, mask).shape == deep(frame, None).shape == frame.shape

    net = bisenet()
    assert parse(frame, net).shape == frame.shape[:2]

    class FakeFace:  # a face hanging off the top-left corner: crop must be padded and paste clipped
        def detect(self, _):
            pts = [SimpleNamespace(x=0.05 + 0.2 * np.cos(a), y=0.05 + 0.2 * np.sin(a)) for a in np.linspace(0, 6.28, 50)]
            return SimpleNamespace(face_landmarks=[pts])

    x, y, side = face_box(FakeFace().detect(None).face_landmarks[0], 320, 240)
    assert x < 0 and y < 0 and side > 0
    assert face_mask(frame, FakeFace(), net).shape == frame.shape[:2]

    fake = np.zeros((240, 320), np.uint8)
    fake[60:180, 100:220] = 1  # skin
    fake[90:110, 110:210] = GLASSES
    shown = face(frame, fake)
    assert (np.abs(shown.astype(int) - np.array(CYAN)).sum(axis=2) < 60).any(), "glasses outline should be cyan"
    assert face(frame, None).shape == frame.shape

    bg = Background(lambda f: f.sum())
    bg.frame = frame
    for _ in range(200):
        if bg.result is not None:
            break
        time.sleep(0.01)
    assert bg.result == frame.sum()
    print("selftest OK")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", nargs="?", choices=["classical", "deep", "face", "compare"])
    p.add_argument("--camera", type=int, default=0)
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()
    if a.selftest:
        selftest()
    elif a.mode:
        run(a.mode, a.camera)
    else:
        p.print_help()
