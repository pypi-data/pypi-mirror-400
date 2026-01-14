import os
import numpy as np
from PIL import Image
import torch
import torchvision
from visaionlibrary.utils.yoloe import YOLOE
from visaionlibrary.utils.yoloe.models.yolo.yoloe.predict_vp import YOLOEVPSegPredictor


class YoloE:
    def __init__(self, model_path="yoloe-v8l-seg.pt", device="cuda:0"):
        VISAION_DIR = os.getenv("VISAION_DIR")
        if VISAION_DIR is None:
            raise ValueError("VISAION_DIR is not set")
        self.model_path = os.path.join(VISAION_DIR, "weights", model_path)
        self.device = device
        self.model = YOLOE(self.model_path)
        self.model.to(self.device)

    def _apply_nms(self, class_names, confidence, bboxes, masks, iou_threshold=0.5):
        """
        Apply Non-Maximum Suppression (NMS) to filter overlapping bounding boxes.
        
        Args:
            class_names: list[str] - List of class names for each detection
            confidence: np.ndarray - Confidence scores, shape (N,)
            bboxes: np.ndarray - Bounding boxes in xyxy format, shape (N, 4)
            masks: np.ndarray or None - Masks data, shape (N, H, W) or None
            iou_threshold: float - IoU threshold for NMS (default: 0.6)
            
        Returns:
            tuple: (filtered_class_names, filtered_confidence, filtered_bboxes, filtered_masks)
        """
        if len(bboxes) == 0:
            return class_names, confidence, bboxes, masks
        
        # Convert to torch tensors
        bboxes_tensor = torch.from_numpy(bboxes).float()
        confidence_tensor = torch.from_numpy(confidence).float()
        
        # Group by class and apply NMS per class
        unique_classes = list(set(class_names))
        keep_indices = []
        
        for cls in unique_classes:
            # Get indices for this class
            cls_indices = [i for i, name in enumerate(class_names) if name == cls]
            
            if len(cls_indices) == 0:
                continue
            
            # Get boxes and scores for this class
            cls_boxes = bboxes_tensor[cls_indices]
            cls_scores = confidence_tensor[cls_indices]
            
            # Sort by confidence (descending)
            sorted_idx = torch.argsort(cls_scores, descending=True)
            cls_boxes = cls_boxes[sorted_idx]
            cls_scores = cls_scores[sorted_idx]
            cls_indices_sorted = [cls_indices[i] for i in sorted_idx]
            
            # Apply NMS
            if len(cls_boxes) > 0:
                keep = torchvision.ops.nms(cls_boxes, cls_scores, iou_threshold)
                # Convert keep indices back to original indices
                # keep is a tensor of indices relative to sorted cls_boxes
                # cls_indices_sorted contains the original indices in sorted order
                keep_numpy = keep.cpu().numpy()
                keep_indices.extend([cls_indices_sorted[i] for i in keep_numpy])
        
        # Sort keep_indices to maintain order (by original index)
        keep_indices = sorted(keep_indices)
        
        # Filter all arrays
        filtered_class_names = [class_names[i] for i in keep_indices]
        filtered_confidence = confidence[keep_indices]
        filtered_bboxes = bboxes[keep_indices]
        
        if masks is not None:
            filtered_masks = masks[keep_indices]
        else:
            filtered_masks = None
        
        return filtered_class_names, filtered_confidence, filtered_bboxes, filtered_masks

    def get_visual_pe(self, prompt_images:list[Image.Image], prompt_boxes:dict[str, list[np.ndarray]], prompt_names:list[str], **kwargs):
        """
        Get visual prompt embeddings from prompt images.
        Args:
            prompt_images: list[Image.Image]
            prompt_boxes: dict[str, list[np.ndarray]]
            prompt_names: list[str]
            **kwargs: dict
        Returns:
            prompt_names: list[list[str]] - flattened list of all class names
            visual_pe: list[np.ndarray] - list of visual prompt embeddings
        """
        assert "bboxes" in prompt_boxes and "cls" in prompt_boxes, f"prompt_boxes must contain 'bboxes' and 'cls'"
        assert len(prompt_images) == len(prompt_boxes["bboxes"]) == len(prompt_boxes["cls"]) == len(prompt_names), f"the length of prompt_image, prompt_boxes['bboxes'], prompt_boxes['cls'], and prompt_names must be the same"

        visual_pe_list = []
        for prompt_image, prompt_box, prompt_cls, prompt_name in zip(prompt_images, prompt_boxes["bboxes"], prompt_boxes["cls"], prompt_names):
            visual_prompt = dict(
                bboxes=prompt_box,
                cls=prompt_cls,
            )

            # Reset predictor before getting vpe to ensure YOLOEVPSegPredictor is used
            self.model.predictor = None
            self.model.predict(prompt_image, prompts=visual_prompt, predictor=YOLOEVPSegPredictor, return_vpe=True, **kwargs)
            # Get vpe from predictor immediately
            vpe = self.model.predictor.vpe
            vpe_np = vpe.detach().cpu().numpy()
            visual_pe_list.append(vpe_np)
        
        return prompt_names, visual_pe_list

    def visual(self, images:list[Image.Image], prompt_names:list[list[str]], visual_pe:list[np.ndarray], **kwargs):
        """
        Predict the visual prompt of the images.
        Args:
            images: list[Image.Image]
            prompt_names: list[list[str]]
            visual_pe: list[np.ndarray]
            **kwargs: dict
        Returns:
            list[Image.Image]
            list[str]
            list[float]
            list[list[float]]
            list[list[list[float]]]
        """
        assert len(prompt_names) == len(visual_pe), f"the length of prompt_names and visual_pe must be the same"

        # Get batch_size from kwargs, default to 8 to avoid OOM
        batch_size = kwargs.pop('batch_size', 8)
        
        for prompt_name, vpe_np in zip(prompt_names, visual_pe):
            vpe = torch.from_numpy(vpe_np).to(self.device)
            self.model.set_classes(prompt_name, vpe)
            self.model.predictor = None  # Reset predictor to apply new class count
            # Disable fuse when class count changes to avoid shape mismatch
            
            # Process images in batches to avoid OOM
            total_images = len(images)
            for batch_start in range(0, total_images, batch_size):
                batch_end = min(batch_start + batch_size, total_images)
                batch_images = images[batch_start:batch_end]
                
                # Process batch
                results = self.model.predict(batch_images, save=False, fuse=False, **kwargs)
                
                # Yield results with correct image_index
                for batch_idx, result in enumerate(results):
                    image_index = batch_start + batch_idx
                    classes_index = result.boxes.cls.detach().cpu().numpy()
                    class_names = [prompt_name[int(class_index)] for class_index in classes_index]
                    confidence = result.boxes.conf.detach().cpu().numpy()
                    bboxes = result.boxes.xyxy.detach().cpu().numpy()
                    if result.masks is not None:
                        masks = result.masks.cpu().numpy()
                    else:
                        masks = None
                
                # Apply NMS to filter overlapping boxes (iou_threshold=0.5)
                class_names, confidence, bboxes, masks = self._apply_nms(
                    class_names, confidence, bboxes, masks, iou_threshold=0.5
                )
                
                yield image_index, class_names, confidence, bboxes, masks
                
                # Clear GPU cache after each batch to free memory
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

    def get_text_pe(self, prompt:list[str], **kwargs):
        """
        Predict the text prompt of the images.
        Args:
            prompt: list[str]
            **kwargs: dict
        Returns:
            np.ndarray
        """
        assert self.model is not None, "Model is not initialized"
        text_pe = self.model.get_text_pe(prompt)
        text_pe = text_pe.detach().cpu().numpy()
        return prompt, text_pe

    def text(self, images:list[Image.Image], prompt:list[str], text_pe:np.ndarray, **kwargs):
        """
        Predict the visual prompt of the images.
        Args:
            images: list[Image.Image]
            prompt: list[str]
            **kwargs: dict
        Returns:
            list[Image.Image]
            list[str]
            list[float]
            list[list[float]]
            list[list[list[float]]]
        """
        text_pe = torch.from_numpy(text_pe).to(self.device)
        assert text_pe.ndim == 3, "text_pe must be a 3D tensor"
        self.model.set_classes(prompt, text_pe)
        self.model.predictor = None  # Reset predictor to apply new class count
        # Disable fuse when class count changes to avoid shape mismatch
        
        # Get batch_size from kwargs, default to 8 to avoid OOM
        batch_size = kwargs.pop('batch_size', 8)
        
        # Process images in batches to avoid OOM
        total_images = len(images)
        for batch_start in range(0, total_images, batch_size):
            batch_end = min(batch_start + batch_size, total_images)
            batch_images = images[batch_start:batch_end]
            
            # Process batch
            results = self.model.predict(batch_images, verbose=False, fuse=False, **kwargs)
            
            # Yield results with correct image_index
            for batch_idx, result in enumerate(results):
                image_index = batch_start + batch_idx
                classes_index = result.boxes.cls.detach().cpu().numpy()
                class_names = [prompt[int(class_index)] for class_index in classes_index]
                confidence = result.boxes.conf.detach().cpu().numpy()
                bboxes = result.boxes.xyxy.detach().cpu().numpy()
                if result.masks is not None:
                    masks = result.masks.cpu().numpy()
                else:
                    masks = None
                
                # Apply NMS to filter overlapping boxes (iou_threshold=0.5)
                class_names, confidence, bboxes, masks = self._apply_nms(
                    class_names, confidence, bboxes, masks, iou_threshold=0.5
                )
                
                yield image_index, class_names, confidence, bboxes, masks
            
            # Clear GPU cache after each batch to free memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def predict(self, images:list[Image.Image], prompt_names:list[list[str]], pe:list[np.ndarray], **kwargs):
        """
        Predict the mixed prompt of the images.
        Args:
            images: list[Image.Image]
            prompt_names: list[list[str]]
            pe: list[np.ndarray]
            **kwargs: dict
        Returns:
            list[Image.Image]
            list[str]
            list[float]
            list[list[float]]
            list[list[list[float]]]
        """
        assert len(prompt_names) == pe.shape[1], f"the length of prompt_names and pe must be the same"

        # Get batch_size from kwargs, default to 8 to avoid OOM
        batch_size = kwargs.pop('batch_size', 8)

        pe = torch.from_numpy(pe).to(self.device)
        self.model.set_classes(prompt_names, pe)
        self.model.predictor = None  # Reset predictor to apply new class count
        # Disable fuse when class count changes to avoid shape mismatch

        # Process images in batches to avoid OOM
        total_images = len(images)
        for batch_start in range(0, total_images, batch_size):
            batch_end = min(batch_start + batch_size, total_images)
            batch_images = images[batch_start:batch_end]
            
            # Process batch
            results = self.model.predict(batch_images, save=False, fuse=False, **kwargs)
            
            # Yield results with correct image_index
            for batch_idx, result in enumerate(results):
                image_index = batch_start + batch_idx
                classes_index = result.boxes.cls.detach().cpu().numpy()
                class_names = [prompt_names[int(class_index)] for class_index in classes_index]
                confidence = result.boxes.conf.detach().cpu().numpy()
                bboxes = result.boxes.xyxy.detach().cpu().numpy()
                if result.masks is not None:
                    masks = result.masks.cpu().numpy()
                else:
                    masks = None
                
                # Apply NMS to filter overlapping boxes (iou_threshold=0.5)
                class_names, confidence, bboxes, masks = self._apply_nms(
                    class_names, confidence, bboxes, masks, iou_threshold=0.5
                )
                
                yield image_index, class_names, confidence, bboxes, masks
            
            # Clear GPU cache after each batch to free memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
AILabel = YoloE