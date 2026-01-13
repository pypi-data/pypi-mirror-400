"""
Example usage of image detection in veridex.

This example demonstrates how to use the image detection module
to analyze images for AI-generated content.
"""

def example_frequency_domain():
    """Example: Frequency domain spectral analysis."""
    from veridex.image import FrequencySignal
    
    print("=" * 60)
    print("Frequency Domain Detection (Spectral Analysis)")
    print("=" * 60)
    
    # Initialize detector
    detector = FrequencySignal()
    
    # Analyze an image
    image_path = "./samples/image/cat_ai.jpg"
    
    result = detector.run(image_path)
    
    if result.error:
        print(f"\n⚠️  Error: {result.error}")
        print("   Make sure the image file exists and PIL is installed")
        print("   Install: pip install veridex[image]")
    else:
        print(f"\nAI Probability: {result.score:.2f}")
        print(f"Confidence: {result.confidence:.2f}")
        
        print(f"\nSpectral Features:")
        for key, value in result.metadata.items():
            if isinstance(value, (int, float)):
                print(f"  {key}: {value:.2f}")
        
        # Interpretation
        print(f"\n💡 Analysis:")
        if result.score > 0.7:
            print("   High probability of AI generation detected")
            print("   Check for anomalous frequency patterns")
        elif result.score > 0.4:
            print("   Moderate suspicion - may be AI-generated or edited")
        else:
            print("   Likely a real photograph")


def example_ela():
    """Example: Error Level Analysis (ELA) for manipulation detection."""
    from veridex.image import ELASignal
    
    print("\n" + "=" * 60)
    print("ELA Detection (Error Level Analysis)")
    print("=" * 60)
    
    detector = ELASignal()
    
    # Analyze an image
    image_path = "./samples/image/cat_ai.jpg" # Or any image
    
    result = detector.run(image_path)
    
    if result.error:
         print(f"⚠️  Error: {result.error}")
    else:
        print(f"\nAI/Manipulation Probability: {result.score:.2f}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Metrics:")
        print(f"  Mean Difference: {result.metadata['ela_mean_diff']:.2f}")
        print(f"  Max Difference: {result.metadata['ela_max_diff']:.2f}")
        
        print(f"\n💡 Interpretation:")
        if result.score > 0.5:
            print("   Higher error levels suggest manipulation or high-freq noise (common in AI)")
        else:
            print("   Consistent error levels suggest original/unmodified image")


def example_dire():
    """Example: DIRE (Diffusion Reconstruction Error) detection."""
    from veridex.image import DIRESignal
    
    print("\n" + "=" * 60)
    print("DIRE Detection (Diffusion Reconstruction)")
    print("=" * 60)
    
    # Initialize with Stable Diffusion model
    detector = DIRESignal(
        model_id="runwayml/stable-diffusion-v1-5",
        timestep=100  # Noise timestep for reconstruction
    )
    
    image_path = "path/to/test_image.jpg"
    
    result = detector.run(image_path)
    
    if result.error:
        print(f"\n⚠️  Error: {result.error}")
        print("   DIRE requires:")
        print("   1. GPU with CUDA support (recommended)")
        print("   2. diffusers library: pip install veridex[image]")
        print("   3. ~4GB disk space for Stable Diffusion model")
    else:
        print(f"\nAI Probability: {result.score:.2f}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Reconstruction Error: {result.metadata.get('reconstruction_error', 'N/A')}")
        
        # Interpretation
        print(f"\n💡 How DIRE Works:")
        print("   • Adds noise to the image")
        print("   • Tries to denoise using a diffusion model")
        print("   • AI images reconstruct better (lower error)")
        print("   • Real photos have higher reconstruction error")


def example_multi_image_analysis():
    """Example: Analyzing multiple images in a directory."""
    from veridex.image import FrequencySignal
    from pathlib import Path
    
    print("\n" + "=" * 60)
    print("Batch Image Analysis")
    print("=" * 60)
    
    # Example image directory
    image_dir = Path("path/to/images/")
    image_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    
    detector = FrequencySignal()
    
    # Mock example since we don't have real images
    example_images = [
        "photo1.jpg",
        "generated_art.png",
        "screenshot.png",
    ]
    
    print(f"\nAnalyzing images from: {image_dir}")
    print("-" * 60)
    
    for img_name in example_images:
        img_path = image_dir / img_name
        
        # In real usage, you would do:
        # result = detector.run(str(img_path))
        
        # Mock result for demonstration
        print(f"\n{img_name}:")
        print(f"  Status: Would analyze this file")
        print(f"  Path: {img_path}")
        
    print("\n💡 Usage:")
    print("   Replace 'path/to/images/' with your actual directory")
    print("   The detector will process each image and return results")


def example_image_preprocessing():
    """Example: Preprocessing images before detection."""
    print("\n" + "=" * 60)
    print("Image Preprocessing Example")
    print("=" * 60)
    
    print("\n💡 Best Practices:")
    print("  1. Use original, uncompressed images when possible")
    print("  2. Avoid heavily edited or filtered images")
    print("  3. Minimum resolution: 256x256 pixels")
    print("  4. Supported formats: PNG, JPEG, WebP")
    
    # Example preprocessing with PIL
    try:
        from PIL import Image
        import numpy as np
        
        print("\n📝 Example Preprocessing Code:")
        print("""
        from PIL import Image
        
        # Load image
        img = Image.open("photo.jpg")
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize if too large (optional)
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size))
        
        # Save for analysis
        img.save("preprocessed.png")
        
        # Now analyze
        from veridex.image import FrequencySignal
        detector = FrequencySignal()
        result = detector.run("preprocessed.png")
        """)
        
    except ImportError:
        print("\n⚠️  PIL not installed")
        print("   Install: pip install veridex[image]")


def example_watermark_detection():
    """Example: Detecting watermarks (future feature)."""
    print("\n" + "=" * 60)
    print("Watermark Detection (Planned Feature)")
    print("=" * 60)
    
    print("\n🚧 Coming Soon:")
    print("  • Invisible watermark detection (DWT/DCT)")
    print("  • Stable Signature extraction")
    print("  • C2PA manifest verification")
    
    print("\n💡 Current Workaround:")
    print("  Use frequency analysis to detect some watermarks:")
    print("""
    from veridex.image import FrequencySignal
    
    detector = FrequencySignal()
    result = detector.run("watermarked_image.png")
    
    # Watermarks may show up as frequency anomalies
    if result.metadata.get('high_freq_anomaly', 0) > threshold:
        print("Possible watermark detected")
    """)


def example_comparison():
    """Example: Comparing real vs AI-generated images."""
    print("\n" + "=" * 60)
    print("Real vs AI-Generated Comparison")
    print("=" * 60)
    
    comparison_data = [
        {
            "name": "Real Photo (DSLR)",
            "score": 0.15,
            "features": "Natural noise, varied frequencies, lens artifacts"
        },
        {
            "name": "AI-Generated (Midjourney)",
            "score": 0.85,
            "features": "Smooth textures, frequency roll-off, no sensor noise"
        },
        {
            "name": "AI-Generated (Stable Diffusion)",
            "score": 0.78,
            "features": "Characteristic spectral pattern, high-freq suppression"
        },
        {
            "name": "Real Photo (iPhone)",
            "score": 0.25,
            "features": "Computational photography artifacts, natural scene"
        },
    ]
    
    print("\nTypical Detection Results:\n")
    for item in comparison_data:
        icon = "🤖" if item["score"] > 0.5 else "📷"
        print(f"{icon} {item['name']}")
        print(f"   AI Probability: {item['score']:.2f}")
        print(f"   Characteristics: {item['features']}\n")
    
    print("💡 Key Differences:")
    print("  • Real photos: Sensor noise, lens distortion, natural compression")
    print("  • AI images: Smooth gradients, perfect symmetry, unnatural lighting")


if __name__ == "__main__":
    print("=" * 60)
    print("IMAGE DETECTION EXAMPLES")
    print("=" * 60)
    
    # 1. Frequency domain analysis
    example_frequency_domain()
    
    # 2. ELA Detection (Error Level Analysis)
    example_ela()
    
    # 3. DIRE detection (requires GPU + diffusers)
    # example_dire()  # Uncomment if you have a GPU
    
    # 3. Batch analysis
    example_multi_image_analysis()
    
    # 4. Preprocessing tips
    example_image_preprocessing()
    
    # 5. Watermark detection (planned)
    example_watermark_detection()
    
    # 6. Comparison guide
    example_comparison()
    
    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  • Use FrequencyDomain for fast CPU-based detection")
    print("  • Use DIRE for highest accuracy (requires GPU)")
    print("  • Process original images, not screenshots")
    print("  • Combine with metadata analysis (EXIF, C2PA)")
    print("\n📚 Learn More:")
    print("  • See README.md for installation")
    print("  • See research doc for technical details")
