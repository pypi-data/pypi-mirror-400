from typing import Optional, Literal
import httpx

from ..common.settings import SdkSettings
from ..modeling.basics import SerializedAlert
from ..common.common_utils import check_package_installed


FlowchartRenderer = Literal['markdown', 'kroki_svg', 'kroki_png']


def display_flowchart(flowchart_script, *, renderer: Optional[FlowchartRenderer] = None):
    settings = SdkSettings.instance()
    if renderer is None:
        renderer = settings.default_flowchart_renderer  # pyright: ignore [reportAssignmentType]
    if not check_package_installed('IPython'):
        raise ImportError('IPython package is not installed. Please install Jupyter kernel')
    if renderer == 'markdown':
        from IPython.display import display, Markdown, clear_output  # pyright: ignore [reportMissingImports]

        clear_output(wait=True)
        display(Markdown('```mermaid\n' + flowchart_script + '\n```'))
    elif renderer == 'kroki_svg' or renderer == 'kroki_png':
        from IPython.display import display, SVG, Image, clear_output  # pyright: ignore [reportMissingImports]

        # see https://docs.kroki.io/kroki/setup/http-clients/
        format = 'svg' if renderer == 'kroki_svg' else 'png'
        url = f'https://kroki.io/mermaid/{format}'
        headers = {'Content-Type': 'text/plain'}

        try:
            response = httpx.post(
                url,
                content=flowchart_script,
                headers=headers,
                verify=settings.httpx_verify,
                timeout=settings.httpx_timeout,
            )
        except httpx.RequestError as e:
            raise RuntimeError(
                f'Failed to generate the chart using Kroki: {e}. '
                'You may consider a different flowchart renderer, e.g. "markdown"'
            ) from e

        if response.status_code == 200:
            if renderer == 'kroki_svg':
                display(SVG(response.content))
            elif renderer == 'kroki_png':
                display(Image(response.content))
        else:
            print(f'Error: {response.status_code} - {response.text}')
    else:
        raise ValueError(f'Unsupported flowchart renderer: {renderer}')


def maybe_display_alert(alert: SerializedAlert) -> bool:
    if not check_package_installed('IPython'):
        return False

    from IPython.display import HTML, display  # pyright: ignore [reportMissingImports]
    from IPython import get_ipython  # pyright: ignore [reportPrivateImportUsage, reportMissingImports]

    if get_ipython() is None:
        return False

    content = alert.get('html', alert.get('text', 'no content'))

    alert_type = alert.get('type', 'info').lower()
    bg_color = '#FFFFFF'
    border_color = '#777777'
    if alert_type == 'info':
        border_color = '#1E90FF'
    elif alert_type == 'warning':
        bg_color = '#FFF8E1'
        border_color = '#FFA500'
    elif alert_type == 'error' or alert_type == 'critical':
        bg_color = '#FFF0F0'
        border_color = '#FF4500'

    box = f"""
    <div style="
    border: 12px solid {border_color};
    padding: 24px 24px;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
    line-height: 1.6;
    font-size: 16px;
    background-color: {bg_color};
    ">
    {content}
    </div>
    """
    display(HTML(box))
    return True
