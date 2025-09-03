import platform
import os
from typing import Optional
from chooseAI.recommendation_engine import ModelRecommendationEngine
from chooseAI.parse_ollama import fetch_models, get_all_models
from chooseAI.systemInfo import SystemInformation


class ChooseAI:
    """Main class to handle AI model recommendations"""

    def __init__(self):
        self.system_info = None
        self.models = None
        self.engine = ModelRecommendationEngine()
        self.categories = [
            ("General/Chat", "general llm"),
            ("Code/Programming", "code"),
            ("Vision/Image", "vision"),
            ("Embedding", "embedding")
        ]

    def get_system_info_handler(self) -> SystemInformation:
        """Get the appropriate system info handler"""
        current_os = platform.system().lower()
        if current_os == "linux":
            from chooseAI.linux_system_information import LinuxSystemInformation
            return LinuxSystemInformation()
        elif current_os == "darwin":  # macOS
            from chooseAI.macOS_system_information import MacOSSystemInformation
            return MacOSSystemInformation()
        elif current_os == "windows":
            from chooseAI.windows_system_information import WindowsSystemInformation
            return WindowsSystemInformation()
        else:
            raise OSError(f"Unsupported operating system: {current_os}")

    def fetch_system_info(self):
        """Fetch and store system information"""
        try:
            print("📊 Analyzing your system...")
            system_handler = self.get_system_info_handler()
            self.system_info = system_handler.get_system_info()
        except Exception as e:
            print(f"❌ Error getting system information: {e}")
            raise

    def display_system_info(self):
        """Display system information in a formatted way"""
        print("=" * 60)
        print("SYSTEM INFORMATION")
        print("=" * 60)

        cpu = self.system_info["cpu"]
        gpu = self.system_info["gpu"]
        ram = self.system_info["ram"]
        storage = self.system_info["storage"]

        print(f"🖥️  CPU: {cpu.name}")
        if cpu.physical_cores:
            print(f"   Cores: {cpu.physical_cores} physical, {cpu.logical_cores} logical")
        if cpu.clock_speed_ghz:
            print(f"   Clock Speed: {cpu.clock_speed_ghz} GHz")
        if cpu.error:
            print(f"   ⚠️  Warning: {cpu.error}")

        print(f"\n🎮 GPU: {gpu.name}")
        if gpu.vram_gb > 0:
            print(f"   VRAM: {gpu.vram_gb} GB")
        if gpu.error:
            print(f"   ⚠️  Warning: {gpu.error}")

        print(f"\n💾 RAM: {ram.total_gb} GB")
        if ram.error:
            print(f"   ⚠️  Warning: {ram.error}")

        print(f"\n💿 Storage: {storage.total_gb} GB")
        if storage.error:
            print(f"   ⚠️  Warning: {storage.error}")

        print()

    def fetch_models(self):
        """Fetch and store model information"""
        if not os.path.exists("ollama_models.db"):
            print("📥 Fetching latest model information from Ollama...")
            try:
                fetch_models()
                print("✅ Model database updated successfully!")
            except Exception as e:
                print(f"❌ Error fetching models: {e}")
                raise
        try:
            self.models = get_all_models()
            print(f"📋 Found {len(self.models)} models in database")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise

    def get_recommendations(self, category_type: str, max_results: int = 5):
        """Generate recommendations for a specific category"""
        try:
            return self.engine.recommend_models(
                system_info=self.system_info,
                models=self.models,
                preferred_type=category_type,
                max_results=max_results
            )
        except Exception as e:
            print(f"❌ Error generating recommendations for {category_type}: {e}")
            return []

    def display_recommendations(self, recommendations, category: str):
        """Display model recommendations in a formatted way"""
        if not recommendations:
            print(f"❌ No suitable models found for {category} category.")
            return

        print("=" * 60)
        print(f"MODEL RECOMMENDATIONS - {category.upper()}")
        print("=" * 60)

        for i, rec in enumerate(recommendations, 1):
            model = rec["model"]
            compatibility = rec["compatibility"]

            # Compatibility emoji
            emoji_map = {
                "Excellent": "exc",
                "Good": "g",
                "Fair": "not bad",
                "Possible": "possible",
                "Not Recommended": "naaah"
            }

            emoji = emoji_map.get(compatibility, "⚪")

            print(f"{i}. {emoji} {model['name'].split(" ")[0]} ({compatibility})")
            print(f"   Score: {rec['total_score']:.2f}/1.0 | Size: {rec['model_size']}")
            print()

    def run(self):
        """Main execution method"""
        print("🤖 ChooseAI - AI Model Recommendation System")
        print("Finding the best local AI models for your hardware!\n")

        # Fetch and display system info
        self.fetch_system_info()
        self.display_system_info()

        # Fetch models
        self.fetch_models()

        # Generate and display recommendations for each category
        for category_name, category_type in self.categories:
            print(f"\n🔍 Analyzing models for {category_name}...")
            recommendations = self.get_recommendations(category_type)
            self.display_recommendations(recommendations, category_name)

        print("\n🚀 Ready to run your chosen model with Ollama!")
        print("   Example: ollama run <model_name>")


