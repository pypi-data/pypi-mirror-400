import typing

from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin


class HtmxTemplateResponseMixin(TemplateResponseMixin):
    """
    Renders a partial HTML template depending on HTTP headers.

    `htmx documentation <https://htmx.org/docs/>`_

    """

    partial_template_name: str | None = None
    """
    A partial template rendered by htmx.

    If not provided, :py:attr:`template_name` + '#partial' is used.

    :type: str | None
    :value: None

    """

    def render_to_response(
        self, context: dict[str, typing.Any], **response_kwargs: typing.Any
    ) -> HttpResponse:
        """Sets :py:attr:`template_name` to :py:attr:`partial_template_name` according to request headers."""
        htmx_request = self.request.headers.get("HX-Request", False)
        boosted = self.request.headers.get("HX-Boosted", False)

        if self.partial_template_name is None:
            self.partial_template_name = f"{self.template_name}#partial"
        if htmx_request and not boosted:
            self.template_name = self.partial_template_name
        return super().render_to_response(context, **response_kwargs)
