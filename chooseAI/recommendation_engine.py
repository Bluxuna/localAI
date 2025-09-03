# chooseAI/recommendation_engine.py
from typing import List, Dict, Any, Tuple
import json
import re
from chooseAI.models.cpu import CPUInfo
from chooseAI.models.gpu import GPUInfo
from chooseAI.models.ram import RAMInfo
from chooseAI.models.storage import StorageInfo


class ModelRecommendationEngine:
    def __init__(self):
        self.model_requirements = {
            "1b": {"min_ram": 2, "min_vram": 1, "recommended_ram": 4},
            "3b": {"min_ram": 4, "min_vram": 2, "recommended_ram": 8},
            "7b": {"min_ram": 8, "min_vram": 4, "recommended_ram": 16},
            "13b": {"min_ram": 16, "min_vram": 8, "recommended_ram": 32},
            "34b": {"min_ram": 32, "min_vram": 16, "recommended_ram": 64},
            "70b": {"min_ram": 64, "min_vram": 32, "recommended_ram": 128}
        }

        # Priority weights for different criteria
        self.weights = {
            "memory_fit": 0.4,
            "performance": 0.3,
            "popularity": 0.2,
            "type_match": 0.1
        }

    def extract_model_size(self, model_name: str, sizes: List[Dict]) -> str:
        """Extract model parameter size from name or sizes list"""
        # Try to extract from model name first
        name_match = re.search(r'(\d+(?:\.\d+)?)b', model_name.lower())
        if name_match:
            size_val = float(name_match.group(1))
            return f"{int(size_val)}b" if size_val.is_integer() else f"{size_val}b"

        # Try to extract from sizes list
        if sizes:
            for size_info in sizes:
                if isinstance(size_info, dict) and size_info.get("unit") == "b":
                    size_val = size_info.get("value", 0)
                    return f"{int(size_val)}b" if size_val.is_integer() else f"{size_val}b"

        return "unknown"

    def calculate_memory_score(self, model_size: str, ram_gb: float, vram_gb: float) -> float:
        """Calculate how well the model fits in available memory"""
        if model_size not in self.model_requirements:
            return 0.5  # Default score for unknown sizes

        req = self.model_requirements[model_size]

        # Check if minimum requirements are met
        if ram_gb < req["min_ram"]:
            return 0.1  # Very low score if minimum RAM not met

        # Prefer GPU if available and sufficient
        if vram_gb >= req.get("min_vram", 0):
            if vram_gb >= req["min_vram"] * 1.5:
                return 1.0  # Excellent fit
            else:
                return 0.8  # Good fit

        # Fall back to RAM
        if ram_gb >= req["recommended_ram"]:
            return 0.7
        elif ram_gb >= req["min_ram"] * 1.5:
            return 0.6
        else:
            return 0.3

    def calculate_performance_score(self, cpu_info: CPUInfo, gpu_info: GPUInfo, model_size: str) -> float:
        score = 0.0

        # CPU contribution
        if cpu_info.physical_cores:
            if cpu_info.physical_cores >= 8:
                score += 0.3
            elif cpu_info.physical_cores >= 4:
                score += 0.2
            else:
                score += 0.1

        # Clock speed
        if cpu_info.clock_speed_ghz:
            if cpu_info.clock_speed_ghz >= 3.0:
                score += 0.2
            elif cpu_info.clock_speed_ghz >= 2.5:
                score += 0.15
            else:
                score += 0.1

        # GPU  (if available)
        if gpu_info.vram_gb > 0 and "No GPU" not in gpu_info.name:
            if gpu_info.vram_gb >= 8:
                score += 0.5  # Excellent GPU
            elif gpu_info.vram_gb >= 4:
                score += 0.3  # Good GPU
            else:
                score += 0.1  # Basic GPU

        return min(score, 1.0)

    def calculate_popularity_score(self, pulls: int) -> float:
        """Calculate popularity score based on number of pulls"""
        if pulls is None or pulls == 0:
            return 0.1

        # Logarithmic scale for popularity
        if pulls >= 10_000_000:
            return 1.0
        elif pulls >= 1_000_000:
            return 0.8
        elif pulls >= 100_000:
            return 0.6
        elif pulls >= 10_000:
            return 0.4
        else:
            return 0.2

    def calculate_type_match_score(self, model_type: str, preferred_type: str = None) -> float:
        """Calculate how well model type matches user preference"""
        if not preferred_type:
            return 0.5

        if model_type.lower() == preferred_type.lower():
            return 1.0
        elif "general" in model_type.lower() and preferred_type.lower() in ["chat", "general"]:
            return 0.8
        else:
            return 0.3

    def recommend_models(self,
                         system_info: Dict[str, Any],
                         models: List[Dict],
                         preferred_type: str = None,
                         max_results: int = 10) -> List[Dict]:
        """
        Recommend best models based on system specifications

        Args:
            system_info: Dictionary containing CPU, GPU, RAM, Storage info
            models: List of available models
            preferred_type: Preferred model type (e.g., 'general', 'code', 'vision')
            max_results: Maximum number of recommendations to return

        Returns:
            List of recommended models with scores
        """
        cpu_info = system_info.get("cpu")
        gpu_info = system_info.get("gpu")
        ram_info = system_info.get("ram")
        storage_info = system_info.get("storage")

        if not all([cpu_info, gpu_info, ram_info, storage_info]):
            raise ValueError("Incomplete system information provided")

        recommendations = []

        for model in models:
            try:
                # Extract model size
                sizes = model.get("metadata", {}).get("sizes", [])
                model_size = self.extract_model_size(model["name"], sizes)

                # Skip if we can't determine size and it's likely too large
                if model_size == "unknown" and any(x in model["name"].lower() for x in ["70b", "65b", "180b"]):
                    continue

                # Calculate individual scores
                memory_score = self.calculate_memory_score(
                    model_size, ram_info.total_gb, gpu_info.vram_gb
                )

                performance_score = self.calculate_performance_score(
                    cpu_info, gpu_info, model_size
                )

                popularity_score = self.calculate_popularity_score(
                    model.get("stats", {}).get("pulls", 0)
                )

                type_match_score = self.calculate_type_match_score(
                    model.get("metadata", {}).get("type", ""), preferred_type
                )

                # Calculate weighted total score
                total_score = (
                        memory_score * self.weights["memory_fit"] +
                        performance_score * self.weights["performance"] +
                        popularity_score * self.weights["popularity"] +
                        type_match_score * self.weights["type_match"]
                )

                # Skip models with very low memory scores (likely won't run)
                if memory_score < 0.2:
                    continue

                recommendations.append({
                    "model": model,
                    "total_score": total_score,
                    "scores": {
                        "memory_fit": memory_score,
                        "performance": performance_score,
                        "popularity": popularity_score,
                        "type_match": type_match_score
                    },
                    "model_size": model_size,
                    "compatibility": self._get_compatibility_status(memory_score, performance_score)
                })

            except Exception as e:
                # Skip models that cause errors
                continue

        # Sort by total score and return top results
        recommendations.sort(key=lambda x: x["total_score"], reverse=True)
        return recommendations[:max_results]

    def _get_compatibility_status(self, memory_score: float, performance_score: float) -> str:
        """Determine compatibility status based on scores"""
        if memory_score >= 0.8 and performance_score >= 0.7:
            return "Excellent"
        elif memory_score >= 0.6 and performance_score >= 0.5:
            return "Good"
        elif memory_score >= 0.4 and performance_score >= 0.3:
            return "Fair"
        elif memory_score >= 0.2:
            return "Possible"
        else:
            return "Not Recommended"

    def explain_recommendation(self, recommendation: Dict) -> str:
        """generate human-readable explanation for a recommendation"""
        model = recommendation["model"]
        scores = recommendation["scores"]
        compatibility = recommendation["compatibility"]

        explanation = f"**{model['name']}** - {compatibility} Match\n"
        explanation += f"Model Size: {recommendation['model_size']}\n"
        explanation += f"Overall Score: {recommendation['total_score']:.2f}/1.0\n\n"

        explanation += "**Score Breakdown:**\n"
        explanation += f"• Memory Compatibility: {scores['memory_fit']:.2f}/1.0\n"
        explanation += f"• Performance Expectation: {scores['performance']:.2f}/1.0\n"
        explanation += f"• Popularity: {scores['popularity']:.2f}/1.0\n"
        explanation += f"• Type Match: {scores['type_match']:.2f}/1.0\n\n"

        if model.get("description"):
            explanation += f"**Description:** {model['description']}\n\n"

        # Add usage recommendation
        if compatibility == "Excellent":
            explanation += "This model should run smoothly on your system."
        elif compatibility == "Good":
            explanation += "This model should run well on your system."
        elif compatibility == "Fair":
            explanation += "This model might run slower but should be usable."
        elif compatibility == "Possible":
            explanation += "This model might be challenging to run efficiently."
        else:
            explanation += "This model is not recommended for your current hardware."

        return explanation