from django.urls import path
from .replicate.genrateimage import  ReplicatePredictionView
from .replicate.trainedmodels import  UserTrainedModelsView
from .replicate.training import  ReplicateModelTrainingView
from .views import GeneratedImageView, ProcessedImageView
from .edit_views.upscaling import UpscaleImageView
from .edit_views.bg_swap import BackgroundReplacementView
from .edit_views.add_accessories import AddAccessoriesView
from .edit_views.objectremovel import ObjectRemoverView
from .edit_views.color_correction import ColorCorrectionView
from .edit_views.outfit_swap import OutfitSwapView
from .Gallery_view.galleryaction import GalleryView
from .paymentgateway.razorpay_gateway import CreateRazorpayOrderView
from .credits_management.creditsviews import CreditsView 
from .credits_management.dedcutcredits import DeductCreditsView 

urlpatterns = [
    path('trainings/', UserTrainedModelsView.as_view()),
    path("predict/", ReplicatePredictionView.as_view()),
    path("train/", ReplicateModelTrainingView.as_view()),
    path("color-correction/", ColorCorrectionView.as_view()),
    path('gallery/', GalleryView.as_view(), name='user-gallery'),
    path("background-remove/",BackgroundReplacementView.as_view()),
    path("outfit-swap/", OutfitSwapView.as_view()),
    path("object-removal/", ObjectRemoverView.as_view(), name="object-removal"),
    path("upscale/", UpscaleImageView.as_view(), name="upscale_image_http"),
    path("add-accessories/", AddAccessoriesView.as_view(), name="add-accessories"),
    path("credits/",CreditsView.as_view(),name="credit views"),
    path("dedctcredit/", DeductCreditsView.as_view(), name="dedcutcredit"),
    path('generated-images/', GeneratedImageView.as_view(), name='generated-images'),
    path('processed-images/', ProcessedImageView.as_view(), name='processed-images'),
    path('create-razorpay-order/', CreateRazorpayOrderView.as_view()),
    
    

]