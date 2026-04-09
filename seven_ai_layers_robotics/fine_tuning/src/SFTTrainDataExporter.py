"""SFT training data exporter for fine-tuning layer.

This module provides functionality to export merged SFT pairs from JSON files
and manage the complete fine-tuning pipeline including training preparation,
training execution, and inference service management.
"""

import json
import random
import string
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from seven_ai_layers_robotics.config import config


class SFTTrainDataExporter:
    """SFT training data exporter for fine-tuning layer.
    
    This class manages the complete fine-tuning pipeline including data export,
    training preparation, training execution, and inference service management.
    
    Attributes:
        base_url: Fine-tuning API base URL.
        script_dir: Script directory path.
        today_dir: Today's data directory.
        merged_json_path: Path to merged SFT pairs JSON file.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        data_file: str = "merged_sft_pairs.json",
    ) -> None:
        """Initialize the SFTTrainDataExporter.
        
        Args:
            base_url: Fine-tuning API base URL. Default: from config.optimization_api
            data_file: Name of the merged SFT pairs JSON file in data directory.
        """
        self.base_url = base_url or config.finetuning_api.base_url
        self.data_dir = Path(__file__).resolve().parent.parent / "data"
        self.merged_json_path = self.data_dir / data_file
        
        # API timeout configuration
        self.prepare_training_timeout = config.finetuning_api.timeout
        self.training_timeout = 300
        self.inference_timeout = 60
        self.status_check_timeout = 30
        
        # Training configuration
        self.base_model_path = config.finetuning_api.base_model_path
        self.dpo_train_config_template = config.finetuning_api.dpo_train_config_template
        self.inference_config_template = config.finetuning_api.inference_config_template

    def _generate_item_name(self, prefix: Optional[str] = None) -> str:
        """Generate a unique item name for training job.
        
        Args:
            prefix: Custom prefix for item name. Uses date + random suffix if None.
            
        Returns:
            Generated item name string.
        """
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = "".join(random.choices(string.ascii_uppercase, k=3))
        
        if prefix:
            return f"{prefix}_{date_str}_{random_suffix}"
        return f"{date_str}_{random_suffix}"

    def validate_data_file(self) -> bool:
        """Validate that the merged SFT pairs JSON file exists.
        
        Returns:
            True if file exists, False otherwise.
        """
        if not self.merged_json_path.exists():
            return False
        return True

    def merge_dataset_files(
        self,
        output_file: str = "merged_sft_pairs.json",
        source_files: Optional[list] = None,
    ) -> Optional[Path]:
        """Merge multiple dataset JSON files into one.
        
        Args:
            output_file: Name of the output merged JSON file.
            source_files: List of source JSON file names to merge. 
                         Default: ["optimized_dataset.json", "single_var_dataset.json"]
            
        Returns:
            Path to merged JSON file if successful, None otherwise.
        """
        if source_files is None:
            source_files = ["optimized_dataset.json", "single_var_dataset.json"]
        
        merged_data = []
        
        for filename in source_files:
            file_path = self.data_dir / filename
            
            if not file_path.exists():
                print(f"Warning: Source file not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):
                        merged_data.extend(data)
                        print(f"Loaded {len(data)} records from {filename}")
                    else:
                        print(f"Warning: {filename} is not a list, skipping")
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing {filename}: {e}")
                continue
            except Exception as e:
                print(f"Error reading {filename}: {type(e).__name__}: {e}")
                continue
        
        if not merged_data:
            print("Error: No data loaded from source files")
            return None
        
        # Write merged data
        output_path = self.data_dir / output_file
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            
            print(f"\nSuccessfully merged {len(merged_data)} total records")
            print(f"Output file: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"Error writing merged file: {type(e).__name__}: {e}")
            return None

    def prepare_training(
        self,
        item_name: Optional[str] = None,
        json_path: Optional[str] = None,
        base_model_path: Optional[str] = None,
        dpo_train_config_template: Optional[str] = None,
        inference_config_template: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Call training preparation API with merged JSON file.
        
        Args:
            item_name: Training job identifier. Auto-generates if None.
            json_path: Path to merged JSON file. Uses default if None.
            base_model_path: Path to base model on server. Default: None (uses config)
            dpo_train_config_template: Path to DPO training config template. Default: None (uses config)
            inference_config_template: Path to inference config template. Default: None (uses config)
            
        Returns:
            API response JSON if successful, None if failed.
            
        Raises:
            FileNotFoundError: If JSON file does not exist.
        """
        if item_name is None:
            item_name = self._generate_item_name()
        
        if json_path is None:
            json_path = str(self.merged_json_path)
        else:
            json_path = str(json_path)
        
        # Use default configuration (can be overridden if needed)
        if base_model_path is None:
            base_model_path = self.base_model_path
        if dpo_train_config_template is None:
            dpo_train_config_template = self.dpo_train_config_template
        if inference_config_template is None:
            inference_config_template = self.inference_config_template
        
        api_url = f"{self.base_url}/prepare-training"
        
        if not Path(json_path).exists():
            raise FileNotFoundError(f"Merged JSON file does not exist: {json_path}")
        
        data = {
            "item_name": item_name,
            "base_model_path": base_model_path,
            "DPO_train_config_template": dpo_train_config_template,
            "inference_config_template": inference_config_template
        }
        
        with open(json_path, "rb") as f:
            files = {
                "corpora_info": ("merged_sft_pairs.json", f, "application/json")
            }
            
            try:
                response = requests.post(
                    api_url,
                    files=files,
                    data=data,
                    timeout=self.prepare_training_timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 500:
                    print(f"Error: Training API server is not ready or encountered an internal error (HTTP 500)")
                    print(f"Please check if the API server at {self.base_url} is running properly")
                    return None
                else:
                    print(f"Prepare training failed: HTTP {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"Prepare training request timeout ({self.prepare_training_timeout}s)")
                return None
            except requests.exceptions.ConnectionError:
                print(f"Prepare training connection error: Check if {api_url} is reachable")
                return None
            except Exception as e:
                print(f"Prepare training unknown error: {type(e).__name__}: {e}")
                return None

    def run_training(
        self,
        item_name: str,
        gpu_ids: list = None
    ) -> bool:
        """Start training job.
        
        Args:
            item_name: Training job identifier.
            gpu_ids: List of GPU IDs to use. Default: [0, 1]
            
        Returns:
            True if training started successfully, False otherwise.
        """
        if gpu_ids is None:
            gpu_ids = [0, 1]
        
        api_url = f"{self.base_url}/run-training"
        payload = {
            "item_name": item_name,
            "gpu_ids": gpu_ids
        }
        
        try:
            response = requests.post(
                api_url,
                json=payload,
                timeout=self.training_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "started":
                    print(f"Training '{item_name}' started successfully.")
                    return True
                else:
                    print(f"Training start failed: {result.get('status', 'unknown')}")
                    return False
            elif response.status_code == 500:
                print(f"Error: Training API server is not ready or encountered an internal error (HTTP 500)")
                print(f"Please check if the API server at {self.base_url} is running properly")
                return False
            else:
                print(f"Training start failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"Training start request timeout ({self.training_timeout}s)")
            return False
        except requests.exceptions.ConnectionError:
            print(f"Training start connection error: Check if {api_url} is reachable")
            return False
        except Exception as e:
            print(f"Training start unknown error: {type(e).__name__}: {e}")
            return False

    def run_inference(
        self,
        item_name: str,
        gpu_id: int = 0,
        api_port: int = 9045
    ) -> bool:
        """Start inference service.
        
        Args:
            item_name: Training job identifier.
            gpu_id: GPU ID to use for inference.
            api_port: Port for inference API service.
            
        Returns:
            True if inference service started successfully, False otherwise.
        """
        api_url = f"{self.base_url}/run-inference"
        payload = {
            "item_name": item_name,
            "gpu_id": gpu_id,
            "api_port": api_port
        }
        
        try:
            response = requests.post(
                api_url,
                json=payload,
                timeout=self.inference_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "started":
                    print(f"Inference service for '{item_name}' started successfully.")
                    return True
                else:
                    print(f"Inference start failed: {result.get('status', 'unknown')}")
                    return False
            elif response.status_code == 500:
                print(f"Error: Inference API server is not ready or encountered an internal error (HTTP 500)")
                print(f"Please check if the API server at {self.base_url} is running properly")
                return False
            else:
                print(f"Inference start failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"Inference start request timeout ({self.inference_timeout}s)")
            return False
        except requests.exceptions.ConnectionError:
            print(f"Inference start connection error: Check if {api_url} is reachable")
            return False
        except Exception as e:
            print(f"Inference start unknown error: {type(e).__name__}: {e}")
            return False

    def check_training_status(self, item_name: str) -> str:
        """Check training job status.
        
        Args:
            item_name: Training job identifier.
            
        Returns:
            Status string: 'finished', 'failed', 'error', 'running', or 'unknown'.
        """
        api_url = f"{self.base_url}/train-finish-check"
        payload = {"item_name": item_name}
        
        try:
            response = requests.get(
                api_url,
                json=payload,
                timeout=self.status_check_timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("status", "unknown").lower()
            else:
                print(f"Status check failed: HTTP {response.status_code}")
                return "unknown"
                
        except requests.exceptions.Timeout:
            print(f"Status check request timeout ({self.status_check_timeout}s)")
            return "unknown"
        except requests.exceptions.ConnectionError:
            print(f"Status check connection error")
            return "unknown"
        except Exception as e:
            print(f"Status check unknown error: {type(e).__name__}: {e}")
            return "unknown"

    def wait_for_training_completion(
        self,
        item_name: str,
        max_wait_minutes: int = 60,
        check_interval: int = 20
    ) -> str:
        """Wait for training to complete with polling.
        
        Args:
            item_name: Training job identifier.
            max_wait_minutes: Maximum minutes to wait.
            check_interval: Seconds between status checks.
            
        Returns:
            Final status string.
            
        Raises:
            TimeoutError: If training exceeds maximum wait time.
        """
        print(f"Waiting for training '{item_name}' to complete (max: {max_wait_minutes} min)...")
        start_time = time.time()
        max_wait_sec = max_wait_minutes * 60
        
        while True:
            status = self.check_training_status(item_name)
            elapsed = (time.time() - start_time) / 60
            print(f"[{time.strftime('%H:%M:%S')}] Status: {status.upper()} | Elapsed: {elapsed:.1f} min")
            
            if status in ("finished", "failed", "error"):
                print(f"\nTraining ended with status: {status.upper()}")
                return status
            
            if time.time() - start_time > max_wait_sec:
                raise TimeoutError(
                    f"Training '{item_name}' has run for more than {max_wait_minutes} minutes."
                )
            
            time.sleep(check_interval)

    def run_pipeline(
        self,
        item_name: Optional[str] = None,
        launch_training: bool = True,
        launch_inference: bool = True,
        max_wait_minutes: int = 60,
        check_interval: int = 20,
        gpu_ids: list = None,
        gpu_id_inference: int = 0,
        api_port_inference: int = 9045
    ) -> Optional[Dict[str, Any]]:
        """Run complete fine-tuning pipeline.
        
        Args:
            item_name: Training job identifier. Auto-generates if None.
            launch_training: Whether to launch training job.
            launch_inference: Whether to launch inference service after training.
            max_wait_minutes: Maximum minutes to wait for training.
            check_interval: Seconds between status checks.
            gpu_ids: GPU IDs for training.
            gpu_id_inference: GPU ID for inference.
            api_port_inference: Port for inference API.
            
        Returns:
            Dictionary with pipeline results if successful, None if failed.
        """
        if item_name is None:
            item_name = self._generate_item_name()
        
        results = {
            "item_name": item_name,
            "prepare_training": False,
            "training": False,
            "inference": False,
            "training_status": "not_started"
        }
        
        # Step 1: Check if merged file exists, if not try to merge
        if not self.validate_data_file():
            print("Merged file not found, attempting to merge source files...")
            merged_path = self.merge_dataset_files()
            if merged_path is None:
                print(f"Error: Merged JSON file not found at {self.merged_json_path}")
                print("Error: And failed to merge source files")
                return None
            print(f"Successfully merged data to: {merged_path}\n")
        else:
            print(f"Using data file: {self.merged_json_path}")
        
        # Step 2: Prepare training
        print("\nStep 1: Preparing training...")
        prepare_result = self.prepare_training(item_name=item_name)
        if prepare_result is None:
            print("Failed to prepare training")
            return None
        results["prepare_training"] = True
        print("Training preparation successful")
        
        # Step 3: Launch training (optional)
        if launch_training:
            print("\nStep 2: Launching training...")
            training_started = self.run_training(item_name, gpu_ids=gpu_ids)
            if not training_started:
                print("Failed to launch training")
                return None
            
            # Step 4: Wait for training completion
            print("\nStep 3: Monitoring training...")
            try:
                final_status = self.wait_for_training_completion(
                    item_name,
                    max_wait_minutes=max_wait_minutes,
                    check_interval=check_interval
                )
                results["training_status"] = final_status
                results["training"] = (final_status == "finished")
            except TimeoutError as e:
                print(f"\nTraining timeout: {e}")
                results["training_status"] = "timeout"
                return None
        else:
            print("\nStep 2: Training launch skipped (launch_training=False)")
        
        # Step 5: Launch inference service (optional)
        if launch_inference:
            print("\nStep 4: Launching inference service...")
            inference_started = self.run_inference(
                item_name,
                gpu_id=gpu_id_inference,
                api_port=api_port_inference
            )
            results["inference"] = inference_started
        else:
            print("\nStep 4: Inference launch skipped (launch_inference=False)")
        
        return results


if __name__ == "__main__":
    exporter = SFTTrainDataExporter()
    
    # Step 1: Merge dataset files
    print("="*60)
    print("Step 1: Merging dataset files...")
    print("="*60)
    merged_path = exporter.merge_dataset_files(
        output_file="merged_sft_pairs.json",
        source_files=["optimized_dataset.json", "single_var_dataset.json"]
    )
    
    if merged_path is None:
        print("\nFailed to merge dataset files")
        exit(1)
    
    # Step 2: Run pipeline
    print("\n" + "="*60)
    print("Step 2: Running fine-tuning pipeline...")
    print("="*60)
    
    results = exporter.run_pipeline(
        launch_training=False,
        launch_inference=False,
        max_wait_minutes=60,
        check_interval=20
    )
    
    if results:
        print(f"\nPipeline completed successfully!")
        print(f"Item name: {results['item_name']}")
        print(f"Prepare training: {results['prepare_training']}")
        print(f"Training: {results['training']}")
        print(f"Training status: {results['training_status']}")
        print(f"Inference: {results['inference']}")
    else:
        print("\nPipeline failed")
