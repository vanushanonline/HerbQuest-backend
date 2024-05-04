
from tensorflow.keras.models import load_model as lm
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from skimage import feature
from PIL import ImageOps
import numpy as np
from PIL import Image, ExifTags
from sklearn.cluster import KMeans
from skimage import feature, morphology
from database import get_herb

def apply_kmeans(image_np, n_clusters=2):
    pixels = image_np.reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(pixels)
    labels = kmeans.labels_
    mask = labels.reshape(image_np.shape[:2])
    
    leaf_cluster = np.argmin([np.linalg.norm(center - [0, 255, 0]) for center in kmeans.cluster_centers_])
    binary_mask = (mask == leaf_cluster).astype(np.uint8)
    
    binary_mask = morphology.remove_small_objects(binary_mask.astype(bool), min_size=500).astype(np.uint8)
    
    return binary_mask

def apply_lbp(image_np, radius=1, n_points=8):
    gray_image = Image.fromarray(image_np).convert('L')
    gray_np = np.array(gray_image)
    lbp = feature.local_binary_pattern(gray_np, n_points, radius, method="uniform")
    return (lbp > np.percentile(lbp, 75)).astype(np.uint8)

def exif_transpose(img):
    if not hasattr(img, '_getexif') or img._getexif() is None:
        return img

    exif = img._getexif()
    orientation = exif.get(0x0112, None) 

    transformations = {
        2: Image.FLIP_LEFT_RIGHT,
        3: Image.ROTATE_180,
        4: Image.FLIP_TOP_BOTTOM,
        5: Image.FLIP_LEFT_RIGHT,
        6: Image.ROTATE_270,
        7: Image.FLIP_LEFT_RIGHT,
        8: Image.ROTATE_90
    }

    return img.transpose(transformations.get(orientation, None)) if orientation in transformations else img

def resize_and_pad(img, target_size=(256, 256)):
    """Resizes the image maintaining its aspect ratio and pads the result to a target size."""
    bbox = ImageOps.crop(img, border=0).getbbox()
    if not bbox:
        return Image.new('RGB', target_size, (0, 0, 0))  # Return black image if no content
    
    cropped = img.crop(bbox)
    ratio = min(target_size[0] / cropped.width, target_size[1] / cropped.height)
    new_size = (int(cropped.width * ratio), int(cropped.height * ratio))
    
    # Resize while maintaining aspect ratio
    img_resized = cropped.resize(new_size, Image.LANCZOS)
    
    # Pad to the target size
    delta_w = target_size[0] - img_resized.width
    delta_h = target_size[1] - img_resized.height
    padding = (delta_w // 2, delta_h // 2, delta_w - (delta_w // 2), delta_h - (delta_h // 2))
    return ImageOps.expand(img_resized, padding, fill=(0, 0, 0))

def prepare_image_for_prediction(image):
    try:

        image = exif_transpose(image)
        image_np = np.array(image)

        kmeans_mask = apply_kmeans(image_np)
        lbp_mask = apply_lbp(image_np)
        combined_mask = np.logical_or(kmeans_mask, lbp_mask).astype(np.uint8)

        combined_mask = morphology.opening(combined_mask, morphology.disk(3))
        combined_mask = morphology.closing(combined_mask, morphology.disk(3))

        segmented_color_image = image_np * np.stack([combined_mask]*3, axis=2)

        if hasattr(image, "_getexif") and image._getexif() is not None:
            exif_data = {ExifTags.TAGS[k]: v for k, v in image._getexif().items() if k in ExifTags.TAGS and isinstance(v, (bytes, str))}
            exif_bytes = ExifTags.dump(exif_data)
        else:
            exif_bytes = None
        
        segmented_img = Image.fromarray(segmented_color_image)
        if exif_bytes:
            segmented_img.info['exif'] = exif_bytes
        new_img = resize_and_pad(segmented_img)
        new_img = np.array(new_img)

        return np.array(new_img)

    except Exception as e:
        print(f"Error processing : {str(e)}")
        return None

herbquest_model = lm('herbquest_model_256.h5')

def get_prediction(img_array):
    
    # Normalize the image (this step may or may not be necessary based on your model training)
    img_array = img_array / 255.0
    
    # Expand dimensions to match the shape the model expects
    img_array = np.expand_dims(img_array, axis=0)
    
    # Get the model's prediction
    predictions = herbquest_model.predict(img_array)

    # Get the highest-probability class label
    predicted_class = np.argmax(predictions[0])
    predicted_confidence = np.max(predictions[0])

    # Map the class label to the class name
    class_names = [
        'ButterflyPea',
        'CommonWireweed',
        'CrownFlower',
        'GreenChireta',
        'HeartLeavedMoonseed',
        'HolyBasil',
        'IndianCopperLeaf',
        'IndianJujube',
        'IndianStingingNettle',
        'IvyGourd',
        'RosaryPea',
        'SmallWaterClover',
        'SpiderWisp',
        'SquareStalkedVine',
        'TrellisVine'
    ]

    predicted_class_name = class_names[predicted_class]

    # Display the prediction probabilities for each class
    print("Prediction Probabilities:")
    for class_name, predicted_probability in zip(class_names, predictions[0]):
        print(f"{class_name}: {predicted_probability * 100:.2f}%")

    return predicted_class

def model(frame):
    image = prepare_image_for_prediction(frame)
    herb_id = get_prediction(image)
    print(herb_id)
    return get_herb(int(herb_id))