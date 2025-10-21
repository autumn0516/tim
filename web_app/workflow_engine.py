"""
Workflow execution engine for video generation
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from video_tool import VideoGenerator

logger = logging.getLogger(__name__)


class WorkflowNode:
    """Base class for workflow nodes"""

    def __init__(self, node_id: str, node_type: str, data: Dict[str, Any]):
        self.node_id = node_id
        self.node_type = node_type
        self.data = data
        self.inputs = {}
        self.output = None

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the node logic"""
        raise NotImplementedError


class ImageNode(WorkflowNode):
    """Node for handling images"""

    def execute(self, context: Dict[str, Any]) -> List[str]:
        """Return list of image paths"""
        images = self.data.get('images', [])
        logger.info(f"ImageNode {self.node_id}: {len(images)} images")
        return images


class TextNode(WorkflowNode):
    """Node for handling text content"""

    def execute(self, context: Dict[str, Any]) -> str:
        """Return text content"""
        text = self.data.get('text', '')
        logger.info(f"TextNode {self.node_id}: {len(text)} characters")
        return text


class AudioNode(WorkflowNode):
    """Node for handling audio"""

    def execute(self, context: Dict[str, Any]) -> Optional[str]:
        """Return audio path"""
        audio = self.data.get('audio')
        logger.info(f"AudioNode {self.node_id}: {audio}")
        return audio


class EffectNode(WorkflowNode):
    """Node for applying effects"""

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Return effect configuration"""
        effect = self.data.get('effect', 'fade')
        params = self.data.get('params', {})
        logger.info(f"EffectNode {self.node_id}: {effect}")
        return {
            'type': effect,
            'params': params
        }


class VideoGeneratorNode(WorkflowNode):
    """Node for generating video"""

    def execute(self, context: Dict[str, Any]) -> str:
        """Generate video and return path"""
        generator = context.get('generator')
        if not generator:
            raise ValueError("No video generator in context")

        # Get inputs from connected nodes
        images = self.inputs.get('images', [])
        text = self.inputs.get('text', '')
        audio = self.inputs.get('audio')
        effects = self.inputs.get('effects', [])

        # Get settings
        settings = self.data.get('settings', {})

        # Build output path
        import uuid
        output_dir = context.get('output_dir', 'web_app/static/uploads/videos')
        output_file = f"workflow_{uuid.uuid4()}.mp4"
        output_path = f"{output_dir}/{output_file}"

        logger.info(f"Generating video: {len(images)} images, {len(text)} chars text")

        # Create base video from images
        if images:
            temp_video = output_path.replace('.mp4', '_temp.mp4')

            generator.create_from_images(
                images=images,
                output=temp_video,
                duration_per_image=settings.get('duration_per_image', 3.0),
                transition=settings.get('transition', 'fade'),
                resolution=settings.get('resolution', (1920, 1080)),
                fps=settings.get('fps', 30)
            )

            current_video = temp_video

            # Apply effects
            for i, effect in enumerate(effects):
                effect_output = output_path.replace('.mp4', f'_effect_{i}.mp4')
                generator.apply_effect(
                    video_path=current_video,
                    effect=effect['type'],
                    output=effect_output,
                    **effect.get('params', {})
                )
                # Clean up previous temp file
                if current_video != temp_video:
                    Path(current_video).unlink(missing_ok=True)
                current_video = effect_output

            # Add audio if provided
            if audio:
                audio_output = output_path.replace('.mp4', '_audio.mp4')
                generator.add_audio(
                    video_path=current_video,
                    audio_path=audio,
                    output=audio_output,
                    volume=settings.get('audio_volume', 0.7)
                )
                # Clean up previous temp file
                Path(current_video).unlink(missing_ok=True)
                current_video = audio_output

            # Add subtitles if text provided
            if text:
                subtitles = self._generate_subtitles(text, len(images),
                                                     settings.get('duration_per_image', 3.0))
                if subtitles:
                    generator.add_subtitles(
                        video_path=current_video,
                        subtitles=subtitles,
                        output=output_path
                    )
                    # Clean up previous temp file
                    if current_video != output_path:
                        Path(current_video).unlink(missing_ok=True)
                else:
                    # Rename to final output
                    import os
                    os.rename(current_video, output_path)
            else:
                # Rename to final output
                import os
                os.rename(current_video, output_path)

            # Clean up temp file
            Path(temp_video).unlink(missing_ok=True)

            logger.info(f"Video generated: {output_path}")
            return output_file

        raise ValueError("No images provided for video generation")

    def _generate_subtitles(self, text: str, num_images: int,
                           duration_per_image: float) -> List[Dict[str, Any]]:
        """Generate subtitle entries from text"""
        if not text:
            return []

        import re
        sentences = re.split('[。！？\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        total_duration = num_images * duration_per_image
        duration_per_subtitle = total_duration / len(sentences)

        subtitles = []
        current_time = 0

        for sentence in sentences:
            subtitles.append({
                'text': sentence,
                'start': current_time,
                'end': current_time + duration_per_subtitle,
                'position': 'bottom'
            })
            current_time += duration_per_subtitle

        return subtitles


class WorkflowEngine:
    """Execute workflows"""

    NODE_TYPES = {
        'image': ImageNode,
        'text': TextNode,
        'audio': AudioNode,
        'effect': EffectNode,
        'video_generator': VideoGeneratorNode,
    }

    def __init__(self):
        self.generator = VideoGenerator()

    def execute(self, workflow: Dict[str, Any]) -> str:
        """
        Execute a workflow

        Args:
            workflow: Workflow definition containing nodes and connections

        Returns:
            Output video filename
        """
        logger.info("Executing workflow...")

        nodes_data = workflow.get('nodes', [])
        connections = workflow.get('connections', [])

        # Create node instances
        nodes = {}
        for node_data in nodes_data:
            node_id = node_data['id']
            node_type = node_data['type']

            node_class = self.NODE_TYPES.get(node_type)
            if not node_class:
                logger.warning(f"Unknown node type: {node_type}")
                continue

            nodes[node_id] = node_class(node_id, node_type, node_data.get('data', {}))

        # Build execution graph
        for conn in connections:
            source_id = conn['source']
            target_id = conn['target']
            input_name = conn.get('targetInput', 'input')

            if source_id in nodes and target_id in nodes:
                # We'll connect during execution
                pass

        # Execute nodes in topological order
        context = {
            'generator': self.generator,
            'output_dir': 'web_app/static/uploads/videos'
        }

        # Simple execution: find the output node and work backwards
        output_node = None
        for node in nodes.values():
            if node.node_type == 'video_generator':
                output_node = node
                break

        if not output_node:
            raise ValueError("No video generator node found in workflow")

        # Execute nodes and collect inputs
        for node_id, node in nodes.items():
            if node.node_type != 'video_generator':
                result = node.execute(context)

                # Find connections to output node
                for conn in connections:
                    if conn['source'] == node_id and conn['target'] == output_node.node_id:
                        input_name = conn.get('targetInput', node.node_type)
                        if node.node_type == 'effect':
                            # Collect effects in a list
                            if 'effects' not in output_node.inputs:
                                output_node.inputs['effects'] = []
                            output_node.inputs['effects'].append(result)
                        else:
                            output_node.inputs[input_name] = result

        # Execute output node
        output_file = output_node.execute(context)

        logger.info(f"Workflow execution complete: {output_file}")
        return output_file
