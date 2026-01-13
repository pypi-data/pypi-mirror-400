import os
import shutil

class Builder:
    def __init__(self):
        pass

    def build(self, project_data, output_dir, mode='clean'):
        """
        Builds the project structure on disk based on the parsed data.
        """
        print(f"Building project in {output_dir} with mode {mode}")
        if mode == 'clean' and os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        os.makedirs(output_dir, exist_ok=True)
        # Placeholder implementation
        pass
