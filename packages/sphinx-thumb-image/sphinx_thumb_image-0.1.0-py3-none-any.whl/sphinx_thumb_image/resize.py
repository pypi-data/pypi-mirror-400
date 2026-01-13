"""Image resizing module."""

from os.path import relpath
from pathlib import Path
from shutil import copyfile

import PIL.Image
import PIL.ImageFile
import PIL.ImageSequence
from docutils.nodes import Element, document
from portalocker import LockException, TemporaryFileLock
from sphinx.application import Sphinx
from sphinx.util import logging

from sphinx_thumb_image.lib import ThumbNodeRequest


class ThumbImageResize:
    """Resize images."""

    THUMBS_SUBDIR = "_thumbs"

    @classmethod
    def save_animated(cls, image: PIL.ImageFile.ImageFile, target: Path, target_size: tuple[int, int]):
        """Save all frames in an animated image file to the target file.

        :param image: Opened source image.
        :param target: Path to target file.
        :param target_size: Image width and height to resize to.
        """
        frames = []
        for frame in PIL.ImageSequence.Iterator(image):
            frame_resized = frame.resize(target_size)
            frames.append(frame_resized)
        disposal = 2  # https://github.com/Robpol86/sphinx-thumb-image/issues/43
        frames[0].save(target, format=image.format, save_all=True, append_images=frames[1:], disposal=disposal)

    @classmethod
    def resize(cls, source: Path, target_dir: Path, request: ThumbNodeRequest, doctree: document, node: Element) -> Path:
        """Resize one image.

        Output image saved with the same relative path as the source image but in the thumbs directory.

        :param source: Path to image file to resize.
        :param target_dir: Path to directory to write resized output image to.
        :param request: Image node's extension request object.
        :param doctree: Current document.
        :param node: Current image node.

        :returns: Path to the output image.
        """
        log = logging.getLogger(__name__)
        with PIL.Image.open(source) as image:
            source_size = image.size
            is_animated = getattr(image, "is_animated", False) and image.n_frames > 1
            # Get target size.
            if is_animated:
                image_copy = image.copy()
                image_copy.thumbnail((request.width or source_size[0], request.height or source_size[1]))
                target_size = image_copy.size
            else:
                image.thumbnail((request.width or source_size[0], request.height or source_size[1]))
                target_size = image.size
            if target_size[0] >= source_size[0]:
                message = f"requested thumbnail size is not smaller than source image ({source_size[0]}x{source_size[1]})"
                doctree.reporter.warning(message, source=node.source, line=node.line)
                copy_instead_of_save = True
            else:
                copy_instead_of_save = False
            # Get target file path.
            thumb_file_name = f"{source.stem}.{target_size[0]}x{target_size[1]}{source.suffix}"
            target = target_dir / thumb_file_name
            if target.exists():
                return target
            # Write to target file path.
            target.parent.mkdir(exist_ok=True, parents=True)
            lock_file = target.parent / f"{target.name}.lock"
            try:
                with TemporaryFileLock(lock_file, timeout=0):
                    if target.exists():
                        return target
                    if copy_instead_of_save:
                        log.debug(f"copying {source} ({source_size[0]}x{source_size[1]}) to {target}")
                        copyfile(source, target)
                    else:
                        log.debug(f"resizing {source} ({source_size[0]}x{source_size[1]}) to {target}")
                        if is_animated:
                            cls.save_animated(image, target, target_size)
                        else:
                            image.save(target, format=image.format)
            except LockException:
                return target
        return target

    @classmethod
    def resize_images_in_document(cls, app: Sphinx, doctree: document):
        """Resize all images in one Sphinx document.

        Called from the doctree-read event.

        :param app: Sphinx application object.
        :param doctree: Current document.
        """
        thumbs_dir = app.env.doctreedir / cls.THUMBS_SUBDIR
        doctree_source = Path(doctree["source"])
        doctree_subdir = doctree_source.parent.relative_to(app.srcdir)
        for node in doctree.findall(lambda n: ThumbNodeRequest.KEY in n):
            imguri = node["uri"]
            if imguri.startswith("data:"):
                doctree.reporter.warning("embedded images (data:...) are not supported", source=node.source, line=node.line)
                continue
            if imguri.find("://") != -1:
                doctree.reporter.warning("external images are not supported", source=node.source, line=node.line)
                continue
            node_uri = Path(imguri)
            if node_uri.is_absolute():
                node_uri = node_uri.relative_to(doctree_source.parent)
            source = doctree_source.parent / node_uri
            if not source.is_file():
                continue  # Subclassed Image directive already emits a warning in this case.
            target_dir = thumbs_dir / doctree_subdir / node_uri.parent
            request: ThumbNodeRequest = node[ThumbNodeRequest.KEY]
            target = cls.resize(source, target_dir, request, doctree, node)
            node["uri"] = relpath(target, start=doctree_source.parent)
