"""
An XBlock for displaying flashcards.

Flashcards XBlock allows the editor to add a list of questions and
answers (separated by a semicolon) which are then displayed as flashcards.
"""

from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Dict, List, Scope, String
from xblock.utils.resources import ResourceLoader


class FlashcardsXBlock(XBlock):
    """
    The FlashcardsXBlock class.

    The content (the values between the <flashcards> tags) is saved as a
    list of flashcard objects and passed as an array to the HTML template.
    """

    loader = ResourceLoader(__name__)
    display_name = String(
        display_name="Display Name",
        default="Flashcards",  # type: ignore[assignment]
        scope=Scope.settings,
        help="The title of the XBlock. It is displayed to the learners.",
    )

    content = List(default=[], scope=Scope.settings, help="List of items")  # type: ignore[assignment]
    styling = Dict(
        default={
            # Warning: consider backward compatibility before making any changes to keys.
            "fontSize": "16px",
            "backgroundColor": "#f8f9fa",
            "textColor": "#212529",
            "borderColor": "#dee2e6",
        },
        scope=Scope.settings,
        help="Configurable styling for the flashcards; more information in the Studio edit view.",
    )

    def student_view(self, context: dict | None = None) -> Fragment:
        """Create fragment and send the appropriate context."""
        context = {
            "title": self.display_name,
            "flashcards": self.content,
            "styling": self.styling,
            "url": self.runtime.local_resource_url(self, "public/student-ui.js"),
        }

        frag = Fragment()
        frag.add_javascript(self.loader.load_unicode("static/js/student.js"))
        frag.add_css_url(self.runtime.local_resource_url(self, "public/student-ui.css"))
        frag.initialize_js("FlashcardsBlock", context)
        return frag

    @classmethod
    def parse_xml(cls, node, runtime, keys, id_generator) -> XBlock:  # noqa: ANN001, ARG003
        """
        Parse the XML for an HTML block.

        The entire subtree under `node` is re-serialized, and set as the
        content of the XBlock.

        The content between the <flashcards> blocks is being transformed
        into a list of flashcard objects, and as such saved into the content class variable
        (which is accessible with self.content)
        """
        block = runtime.construct_xblock_from_class(cls, keys)
        flashcards = []

        flashcards = [
            {"front": element.attrib["front"], "back": element.attrib["back"]} for element in node.iter("flashcard")
        ]

        block.content = flashcards
        block.title = node.attrib["title"]
        return block

    @staticmethod
    def workbench_scenarios() -> list[tuple[str, str]]:
        """A canned scenario for display in the workbench."""
        return [
            (
                "FlashcardsXBlock",
                """<vertical_demo>
                <flashcards title="Capital cities">
<flashcard front="Croatia" back="Zagreb" />
<flashcard front="France" back="Paris" />
                </flashcards>
                </vertical_demo>
             """,
            ),
        ]

    def studio_view(self, context: dict | None = None) -> Fragment:
        """Create a fragment used to display the edit view in the Studio."""
        context = {
            "title": self.display_name,
            "flashcards": self.content,
            "styling": self.styling,
            "url": self.runtime.local_resource_url(self, "public/studio-ui.js"),
        }

        frag = Fragment(self.loader.render_django_template("static/html/studio.html", context=context))
        frag.add_javascript(self.loader.load_unicode("static/js/studio.js"))
        frag.add_css_url(self.runtime.local_resource_url(self, "public/studio-ui.css"))
        frag.initialize_js("FlashcardsEditor", context)
        return frag

    @XBlock.json_handler
    def studio_submit(self, data: dict, suffix: str = "") -> dict[str, str]:  # noqa: ARG002
        """Called when submitting the form in Studio."""
        self.display_name = data.get("title")
        self.content = data.get("flashcards")
        self.styling = data["styling"]
        return {"result": "success"}
