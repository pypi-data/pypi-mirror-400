import gradio as gr
from gradio_tiff import Tiff

demo = gr.Interface(
    lambda x: x,
    inputs=Tiff(value=Tiff().example_value()),
    outputs=Tiff(),
)


if __name__ == "__main__":
    demo.launch()
