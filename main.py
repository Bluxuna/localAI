import platform
import os
from typing import Optional
from chooseAI.recommendation_engine import ModelRecommendationEngine
from chooseAI.parse_ollama import fetch_models, get_all_models
from chooseAI.systemInfo import SystemInformation
from chooseAI.chooseAI import  ChooseAI

if __name__ == "__main__":
    choose_ai = ChooseAI()
    choose_ai.run()
