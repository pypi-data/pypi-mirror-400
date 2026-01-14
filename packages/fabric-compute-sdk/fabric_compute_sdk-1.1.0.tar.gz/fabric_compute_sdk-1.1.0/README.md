# Fabric SDK

**Official Python SDK for Fabric - Distributed AI Compute Network**

Submit AI workloads to the Fabric network programmatically.

## Installation

```bash
pip install fabric-compute-sdk
```

## Quick Start

### Option 1: Email/Password Authentication

```python
from fabric_sdk import FabricClient

# Initialize client with email/password
client = FabricClient(
    api_url="https://api.fabric.carmel.so",
    email="your@email.com",
    password="your_password"
)

# Submit a job
job = client.submit_job(
    workload_type="llm_inference",
    params={
        "prompt": "Explain quantum computing in simple terms",
        "max_length": 200,
        "temperature": 0.7,
        "use_gpu": True
    },
    job_name="My LLM Inference Job"
)

print(f"Job submitted: {job['id']}")

# Wait for completion
result = client.wait_for_job(job['id'], timeout=300)
print(f"Job completed in {result['duration_seconds']}s")
print(f"Cost: ${result['actual_cost']}")
```

### Option 2: API Key Authentication (Recommended for Google OAuth users)

```python
from fabric_sdk import FabricClient

# Initialize client with API key
client = FabricClient(
    api_url="https://api.fabric.carmel.so",
    api_key="fb_live_..."  # Get this from dashboard Settings > API Keys
)

# Works exactly the same!
job = client.submit_job(
    workload_type="llm_inference",
    params={"prompt": "Explain quantum computing"},
    job_name="My Job"
)
```

**Why use API keys?**
- No password needed (great for Google/GitHub OAuth users)
- More secure for CI/CD pipelines
- Easy to rotate and revoke
- Each project can have its own key

## Workflows - Zero-Config Job Submission

Instead of configuring dozens of parameters, use **workflows** - preset configurations for common use cases.

### Bioinformatics Examples

```python
# Sequence alignment - automatically sets all alignment parameters
job = client.submit_job(
    workload_type="ml_preprocess",
    params={
        "data_url": "https://your-bucket.s3.amazonaws.com/sequences.fasta",
        "workflow": "sequence_alignment"
    }
)

# Variant analysis - optimized for genomic variants
job = client.submit_job(
    workload_type="ml_preprocess",
    params={
        "data_url": "https://your-bucket.s3.amazonaws.com/variants.vcf",
        "workflow": "variant_analysis"
    }
)

# Protein property calculation
job = client.submit_job(
    workload_type="ml_preprocess",
    params={
        "data_url": "https://your-bucket.s3.amazonaws.com/proteins.fasta",
        "workflow": "protein_properties"
    }
)
```

### ML Training Examples

```python
# Quick classification - fast training with reasonable defaults
job = client.submit_job(
    workload_type="ml_train",
    params={
        "data_url": "https://your-bucket.s3.amazonaws.com/labeled_data.csv",
        "workflow": "quick_classification"
    }
)

# High accuracy - slower but more thorough hyperparameter search
job = client.submit_job(
    workload_type="ml_train",
    params={
        "data_url": "https://your-bucket.s3.amazonaws.com/labeled_data.csv",
        "workflow": "high_accuracy"
    }
)

# Survival analysis - for time-to-event data
job = client.submit_job(
    workload_type="ml_train",
    params={
        "data_url": "https://your-bucket.s3.amazonaws.com/survival_data.csv",
        "workflow": "survival_analysis"
    }
)
```

### Image Processing Examples

```python
# Cell segmentation - optimized for microscopy images
job = client.submit_job(
    workload_type="image_preprocess",
    params={
        "image_url": "https://your-bucket.s3.amazonaws.com/cells.tiff",
        "workflow": "cell_segmentation_prep"
    }
)

# ImageNet preparation - resize and normalize for deep learning
job = client.submit_job(
    workload_type="image_preprocess",
    params={
        "image_url": "https://your-bucket.s3.amazonaws.com/image.jpg",
        "workflow": "imagenet_prep"
    }
)

# Fluorescence quantification - for DAPI, GFP, etc.
job = client.submit_job(
    workload_type="image_preprocess",
    params={
        "image_url": "https://your-bucket.s3.amazonaws.com/fluorescence.tiff",
        "workflow": "fluorescence_quantification"
    }
)
```

### Image Classification Examples

```python
# Zero-shot classification - classify without training
job = client.submit_job(
    workload_type="image_label",
    params={
        "image_url": "https://your-bucket.s3.amazonaws.com/image.jpg",
        "workflow": "zero_shot_classification",
        "candidate_labels": ["cat", "dog", "bird", "fish"]
    }
)

# Object detection - find and locate objects
job = client.submit_job(
    workload_type="image_label",
    params={
        "image_url": "https://your-bucket.s3.amazonaws.com/image.jpg",
        "workflow": "object_detection"
    }
)
```

### Override Workflow Defaults

Workflows set sensible defaults, but you can override any parameter:

```python
job = client.submit_job(
    workload_type="ml_train",
    params={
        "data_url": "https://...",
        "workflow": "quick_classification",
        # Override specific settings
        "max_iterations": 200,      # More iterations
        "test_size": 0.3,           # Larger test set
        "use_gpu": True             # Force GPU
    }
)
```

### Available Workflow Categories

**ML Preprocessing (25+ workflows)**
- Bioinformatics: sequence_alignment, variant_analysis, protein_properties, phylogenetic_prep
- Sports/Trajectory: trajectory_analysis, play_classification
- General: basic_cleaning, anomaly_detection_prep, clustering_prep

**ML Labeling (12+ workflows)**
- Clustering: quick_clustering, auto_clustering, hierarchical_clustering, density_clustering
- Segmentation: customer_segmentation, fine_segmentation, binary_threshold

**ML Training (20+ workflows)**
- Classification: quick_classification, balanced_classification, high_accuracy, interpretable
- Regression: quick_regression, ridge_regression, lasso_regression
- Neural Nets: neural_net_starter, neural_net_deep
- Specialized: survival_analysis, differential_expression, biomarker_discovery

**ML Inference (10+ workflows)**
- classification_inference, regression_inference, batch_inference, anomaly_scoring

**Image Preprocessing (15+ workflows)**
- Standard: imagenet_prep, object_detection_prep, high_resolution_prep
- Microscopy: fluorescence_quantification, cell_segmentation_prep, dapi_analysis

**Image Labeling (13+ workflows)**
- zero_shot_classification, object_detection, visual_clustering, feature_extraction

**Image Training (12+ workflows)**
- quick_train, balanced_train, resnet_classifier, vit_classifier, cell_image_classifier

**Image Inference (12+ workflows)**
- image_classification, imagenet_resnet50, cell_classification, batch_inference

## Features

- **Dual Authentication** - Email/password OR API keys
- **100+ Workflows** - Preset configurations for common use cases
- **API Key Management** - Create, list, and revoke keys programmatically
- **Job Submission** - Submit 30+ production workload types
- **Batch Submission** - Submit 1000s of jobs in seconds (100x faster!)
- **Custom Workloads** - Upload and run your own Python code
- **Parallel Processing** - Distribute work across multiple nodes
- **Job Monitoring** - Track progress and get results
- **Credit Management** - Check balance and purchase credits
- **Node Discovery** - List available compute nodes
- **Auto-Retry** - Built-in network resilience
- **Type Hints** - Full TypeScript-style typing support

## Supported Workload Types (30+)

**ML Pipeline (8)**
- `ml_preprocess`, `ml_label`, `ml_train`, `ml_inference`
- `image_preprocess`, `image_label`, `image_train`, `image_inference`

**Compute & Simulation (5)**
- `cpu_compute_benchmark`, `gpu_compute_benchmark`
- `eigenvalue_decomposition`, `financial_forecast_simulation`, `agent_simulation`

**Data Processing (5)**
- `data_cleaning`, `feature_extraction`, `csv_vectorization`
- `data_augmentation`, `outlier_detection`

**AI Inference (7)**
- `llm_inference`, `llm_inference_batch`, `image_classification`
- `embedding_generation`, `sentiment_analysis`
- `text_summarization`, `question_answering`

**Media Processing (5)**
- `video_transcode`, `audio_to_text`, `video_object_detection`
- `image_resize_batch`, `video_summarization`

**Web & HTTP (2)**
- `http_microtask`, `custom_python`

## Custom Workloads

Upload and run your own Python code:

```python
# Upload custom workload
workload = client.upload_custom_workload(
    name="my-data-processor",
    description="Process proprietary data format",
    zip_path="./my_workload.zip"
)

# Run it
job = client.submit_job(
    workload_type="custom_python",
    params={
        "custom_workload_id": workload["id"],
        "data_url": "https://..."
    }
)
```

### Parallel Processing

Distribute work across multiple nodes:

```python
workload = client.upload_custom_workload(
    name="batch-processor",
    zip_path="./batch_workload.zip",
    parallel_mode=True,
    files_per_shard=100  # 100 files per node
)

# Submit with 10,000 input files - runs on ~100 nodes in parallel
job = client.submit_job(
    workload_type="custom_python",
    params={"custom_workload_id": workload["id"]}
)
```

## Documentation

Complete documentation, guides, and examples are available in the **[Fabric Dashboard](https://fabric.carmel.so)**.

### Key Resources
- **Workflows Reference** - All 100+ preset workflows
- **Custom Workloads** - Build and deploy your own code
- **ML Pipeline Guide** - End-to-end machine learning
- **API Reference** - Complete endpoint documentation
- **Examples** - Ready-to-run code samples

## Support

Access the **[Fabric Dashboard](https://fabric.carmel.so)** for documentation, support, and account management.

## License

Apache License 2.0

Copyright 2025 Carmel Labs, Inc.
