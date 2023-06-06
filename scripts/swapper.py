import os
from typing import List
import cv2
import insightface
import onnxruntime
import numpy as np
from PIL import Image, ImageFont, ImageDraw, PngImagePlugin
from scripts.faceswap_logging import logger

providers = onnxruntime.get_available_providers()
if "TensorrtExecutionProvider" in providers:
    providers.remove("TensorrtExecutionProvider")


def get_face_single(img_data, face_num=0):
    face_analyser = insightface.app.FaceAnalysis(name="buffalo_l", providers=providers)
    face_analyser.prepare(ctx_id=0, det_size=(640, 640))
    face = face_analyser.get(img_data)
    try:
        return sorted(face, key=lambda x: x.bbox[0])[face_num]
    except IndexError:
        return None


def swap_face(
    source_img : Image, target_img : Image, model : str ="../models/inswapper_128.onnx", face_nums : List[int]=[0]
) -> Image:
    source_img = cv2.cvtColor(np.array(source_img), cv2.COLOR_RGB2BGR)
    target_img = cv2.cvtColor(np.array(target_img), cv2.COLOR_RGB2BGR)
    source_face = get_face_single(source_img, face_num=0)
    if source_face is not None:
        result = target_img
        model_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), model)
        face_swapper = insightface.model_zoo.get_model(
            model_path, providers=providers
        )
        for face_num in face_nums :
            target_face = get_face_single(target_img, face_num=face_num)
            if target_face is not None:
                result = face_swapper.get(
                    result, target_face, source_face, paste_back=True
                )
            else:
                logger.info(f"No target face found")

        numpy_image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        return Image.fromarray(numpy_image)
    else:
        logger.info(f"No source face found")

    return None
