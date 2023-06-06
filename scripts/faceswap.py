import gradio as gr
import modules.scripts as scripts
from modules import scripts, scripts_postprocessing
from modules.processing import StableDiffusionProcessing
from modules.shared import cmd_opts, opts, state
from PIL import Image

from scripts.faceswap_logging import logger
from scripts.swapper import swap_face
from scripts.faceswap_version import version_flag


class FaceSwapScript(scripts.Script):
    def title(self):
        return f"Face Swap {version_flag}"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion(f"Face Swap {version_flag}", open=False):
            with gr.Column():
                img = gr.inputs.Image(type="pil")
                activate = gr.Checkbox(
                    False, placeholder="activate the extension", label="Activate"
                )
                face_nums = gr.Textbox(
                    value="0",
                    placeholder="Which face to swap (comma separated), start from 0",
                    label="Comma separated face number(s)",
                )
        return [img, activate, face_nums]

    def process(self, p: StableDiffusionProcessing, img, activate, face_nums):
        self.source = img
        self.activate = activate
        self.face_num = face_nums
        if self.activate:
            if self.source is not None:
                logger.info(f"Process FaceSwap %s", type(img))

    def postprocess_image(self, p, script_pp: scripts.PostprocessImageArgs, *args):
        if self.activate:
            if self.source is not None:
                face_nums = {
                    int(x) for x in self.face_num.strip(",").split(",") if x.isnumeric()
                }
                if len(face_nums) == 0:
                    face_nums = [0]
                image: Image.Image = script_pp.image
                result = swap_face(self.source, image, face_nums = face_nums)
                pp = scripts_postprocessing.PostprocessedImage(result)
                pp.info = {}
                p.extra_generation_params.update(pp.info)
                script_pp.image = pp.image
