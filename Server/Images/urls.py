"""
Image url configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URL conf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from Images import views

"""
API endpoint creation
"""

urlpatterns = [
    path('<ipfsHash>/', views.ImageDetailView.as_view()),
    path('', views.ImageListView.as_view()),
]

# REFERENCES
# router.get('/', Image.test);
# router.get('/accounts', Image.accounts);
# router.get('/web3-status', Image.webStatus);
# router.get('/files/:name', Image.getData);
# router.get('/images', Image.all);
# router.get('/images/:label', Image.findByLabel);
# // find image by id
# router.get('/images-id/:id', Image.findById);
# /*  upload POST endpoint */
# router.post('/upload', Image.upload.single('file'), Image.uploadFile, Image.postData, Image.create);
# router.get('/getfile/:hash', Image.getFile);