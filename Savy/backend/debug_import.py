import sys
import os

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import models.affiliate
    print("models.affiliate imported successfully")
    print("Attributes:", dir(models.affiliate))
    from models.affiliate import MatchType
    print("MatchType imported successfully:", MatchType)
except Exception as e:
    print("Import Failed:", e)
    import traceback
    traceback.print_exc()
