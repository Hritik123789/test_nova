# Sample Images for Nova 2 Omni Testing

This folder contains sample images for testing the Image Analysis Agent powered by Amazon Nova 2 Omni (multimodal AI).

---

## What Images to Add

### 1. Construction Site Images (3-5 images)
**What to capture**:
- Active construction sites in Mumbai
- Building under construction
- Road construction/repair
- Infrastructure projects
- Scaffolding and equipment

**Where to find**:
- Google Images: Search "Mumbai construction site"
- Unsplash: https://unsplash.com/s/photos/construction
- Pexels: https://www.pexels.com/search/construction/
- Your own photos of Mumbai construction

**Naming convention**: `construction_1.jpg`, `construction_2.jpg`, etc.

---

### 2. Permit Documents (1-2 images)
**What to capture**:
- Building permits
- Construction permits
- BMC approval documents
- MahaRERA certificates
- Any official permit/license documents

**Where to find**:
- Google Images: Search "building permit document"
- Sample permit templates
- Mock permit documents (for testing)

**Naming convention**: `permit_1.jpg`, `permit_document_1.jpg`, etc.

---

### 3. Safety Violations (1-2 images)
**What to capture**:
- Construction sites without safety barriers
- Unsafe scaffolding
- Missing safety equipment
- Hazardous conditions

**Where to find**:
- Google Images: Search "construction safety violation"
- News articles about construction accidents
- Public safety reports

**Naming convention**: `safety_violation_1.jpg`, etc.

---

### 4. BMC Signage (1-2 images)
**What to capture**:
- BMC project boards
- Government signage at construction sites
- Project information boards
- Contractor details boards

**Where to find**:
- Google Images: Search "BMC Mumbai construction board"
- Photos of Mumbai construction sites
- Government project announcements

**Naming convention**: `bmc_signage_1.jpg`, etc.

---

## Supported Formats

- `.jpg` / `.jpeg`
- `.png`

**Recommended**: Use `.jpg` for photos, `.png` for documents

---

## Image Requirements

- **Size**: Any size (will be processed automatically)
- **Quality**: Higher quality = better analysis
- **Content**: Clear, well-lit images work best
- **Orientation**: Any orientation supported

---

## Quick Start: Download Sample Images

### Option 1: Use Unsplash (Free, No Attribution Required)

```bash
# Visit these URLs and download images:
# 1. https://unsplash.com/s/photos/construction-site
# 2. https://unsplash.com/s/photos/building-construction
# 3. https://unsplash.com/s/photos/construction-worker
```

### Option 2: Use Pexels (Free, No Attribution Required)

```bash
# Visit these URLs and download images:
# 1. https://www.pexels.com/search/construction/
# 2. https://www.pexels.com/search/building%20site/
```

### Option 3: Use Google Images

```bash
# Search for:
# - "Mumbai construction site"
# - "building permit document"
# - "construction safety"
```

**Note**: Ensure you have rights to use the images (use royalty-free sources).

---

## Example File Structure

```
sample_images/
├── construction_1.jpg          # High-rise building under construction
├── construction_2.jpg          # Road construction
├── construction_3.jpg          # Infrastructure project
├── permit_document_1.jpg       # Building permit
├── safety_violation_1.jpg      # Unsafe construction site
├── bmc_signage_1.jpg          # BMC project board
└── README.md                   # This file
```

---

## Testing the Image Analysis

Once you've added images:

```bash
python agents/image_analysis_nova.py
```

Expected output:
```
🖼️  Initializing Image Analyzer (Amazon Nova 2 Omni)...
✓ Connected to Amazon Bedrock

📸 Found 6 images to analyze

🔍 Analyzing image: sample_images/construction_1.jpg...
💰 Tokens: 1234, Cost: $0.0050

📊 Analysis for construction_1.jpg:
==================================================
This image shows a large-scale construction site...
[Detailed analysis from Nova 2 Omni]
==================================================

✅ Image analysis complete!
💾 Saved analysis to image_analysis_results.json
💰 Total cost: $0.0300
```

---

## Cost Estimation

**Nova 2 Omni (Nova Pro) Pricing**:
- Input: $0.0006 per 1K tokens
- Output: $0.0048 per 1K tokens

**Per Image**:
- Average: ~1,500 tokens (image + text)
- Cost: ~$0.005 per image

**For 10 Images**:
- Total tokens: ~15,000
- Total cost: ~$0.05

**Well within your $100 budget!**

---

## What Nova 2 Omni Can Detect

### Construction Sites
- Type of construction (building, road, infrastructure)
- Project scale (small, medium, large)
- Equipment visible (cranes, excavators, etc.)
- Safety measures (barriers, helmets, signage)
- Progress stage (foundation, structure, finishing)

### Permit Documents
- Permit number
- Project name and location
- Permit type
- Issue and expiry dates
- Issuing authority
- Special conditions

### Safety Analysis
- Missing safety equipment
- Unsafe conditions
- Violations of safety codes
- Risk assessment

---

## Tips for Best Results

1. **Clear Images**: Use high-resolution, well-lit photos
2. **Focus**: Ensure the subject is in focus
3. **Context**: Include surrounding context for better analysis
4. **Multiple Angles**: Provide different views of the same site
5. **Documents**: Ensure text is readable in permit documents

---

## Troubleshooting

### "No images found"
- Check that images are in `.jpg`, `.jpeg`, or `.png` format
- Ensure images are directly in `sample_images/` folder (not subfolders)

### "Failed to load image"
- Check file permissions
- Ensure image is not corrupted
- Try a different image format

### "Nova API error"
- Check AWS credentials are configured
- Ensure you have access to Nova Pro model
- Check your AWS region is us-east-1

---

## Alternative: Use Placeholder Images

If you don't have real images, you can use these placeholder approaches:

### 1. Create Simple Test Images
```python
from PIL import Image, ImageDraw, ImageFont

# Create a simple construction site image
img = Image.new('RGB', (800, 600), color='lightblue')
draw = ImageDraw.Draw(img)
draw.rectangle([100, 200, 700, 500], fill='gray', outline='black', width=5)
draw.text((300, 350), "CONSTRUCTION SITE", fill='black')
img.save('sample_images/construction_test.jpg')
```

### 2. Download from Free Stock Photo Sites
- Unsplash: https://unsplash.com
- Pexels: https://www.pexels.com
- Pixabay: https://pixabay.com

---

## Next Steps

1. Add 5-10 images to this folder
2. Run `python agents/image_analysis_nova.py`
3. Check `image_analysis_results.json` for results
4. Review cost in `cost_log.json`

**Ready to test Mumbai's visual intelligence!** 📸🤖
