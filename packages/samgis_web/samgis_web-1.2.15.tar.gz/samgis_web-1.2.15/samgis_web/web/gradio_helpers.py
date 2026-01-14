from typing import Callable

import gradio as gr

from samgis_core.utilities.type_hints import ListStr, DictStrInt


def get_example_complete(example_text, example_body, key_text: str = "string_prompt") -> str:
    """
    return an example dict, as in {"string_prompt": "some text..."}

    Args:
        example_text: example text
        example_body: a request example body placeholder
        key_text: dict key for text string

    Returns:
        an example formatted json string request

    """
    import json
    example_dict = dict(**example_body)
    if key_text in example_dict:
        example_dict[key_text] = example_text
    return json.dumps(example_dict)


def get_gradio_interface_geojson(
        fn_inference: Callable, markdown_text: str, examples_text_list_text: ListStr, example_body: DictStrInt):
    """
    Return a Gradio interface composed by a row, two column (one text input and one text output)

    Args:
        fn_inference: function used within the Gradio interface
        markdown_text: Markdown description
        examples_text_list_text: a list of example formatted json string requests
        example_body: a request example body placeholder

    Returns:
        a Gradio interface

    """
    with gr.Blocks() as gradio_app:
        gr.Markdown(markdown_text)

        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(lines=1, placeholder=None, label="Payload input")
                btn = gr.Button(value="Submit")
            with gr.Column():
                text_output = gr.Textbox(lines=1, placeholder=None, label="Geojson Output")

        gr.Examples(
            examples=[
                get_example_complete(example, example_body) for example in examples_text_list_text
            ],
            inputs=[text_input],
        )
        btn.click(
            fn_inference,
            inputs=[text_input],
            outputs=[text_output]
        )
    return gradio_app
