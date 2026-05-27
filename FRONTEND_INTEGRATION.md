# Guide pour l'integration du front end


### 1. Uploader Video
Le front end envoie un message a /video/upload comportant le fichier video et son nom
```javascript
async function uploadVideo(file, title) {
  const formData = new FormData();
  formData.append('original', file);
  formData.append('titre', title);
  const response = await fetch('http://localhost:8000/video/upload/', {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  return data.id; // 
}
```
### 1.2 Uploader watermark
Le front end envoie un message a watermark/upload comportant le fichier image
```javascript
async function uploadVideo(file, title) {
  const formData = new FormData();
  formData.append('image', file);
  const response = await fetch('http://localhost:8000/watermark/upload/', {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  return data.id; // Id de l'image 
}
```

### 2. Traitement de video
le front end envoie une requete a video/processing comportant l'id de la video a traiter, l'action a mener et les parametres necessaires
```javascript
async function processVideo(videoId, action, parameters = {}) {
  const response = await fetch('http://localhost:8000/video/processing/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      action: action,
      parameters: parameters
    })
  });
  const data = await response.json();
  if (response.status === 202) {
    return data.task_id; // 
  }
  throw new Error(data.error);
}
```
exemple:
video_id : 4,
action : trim, (couper)
parameters: {
  start: 00:00:10,
  end: 00:00:30
};  -> coupe la video d'id 4 de 10 a 30 secondes

### 3. verifier  l'etat de traitement
le front end recoit l'etat de la video avec un GET a /video/processing/status/{id}
```javascript
async function checkVideoStatus(videoId) {
  const response =  await fetch(`${BASE_URL}/prototype/video/processing/status/${videoId}/`,{
            method : 'GET',
            headers: { 'Content-Type': 'application/json' },
        });
  const data = await response.json();
  return data.status; // EN ATTENTE, EN COURS DE TRAITEMENT, TERMINE, ECHOUE
}
```

### 4. Exporter la video
Le front end envoie une requete post a video/export comportant l'id de la video a exporter , le format et la qualite
```javascript
async function exportVideo(videoId, format = 'mp4', quality = 'medium') {
  const response = await fetch('http://localhost:8000/video/export/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      format: format,
      quality: quality
    })
  });
  const data = await res.json(); //data (task_id,status)
}
```
### 5.verifier l'etat de l'export
Le front end envoie une requete post a video/export/status/{task_id}/
```javascript
async function checkExportStatus(task_id){
  const res  = await fetch(`http://localhost:8000/video/export/status/${task_id}/`);
      const data = await res.json();
      return data.status; // EN ATTENTE, EN COURS DE TRAITEMENT, TERMINE, ECHOUE
}
```



## Formats
| MP4 | .mp4 
| WebM | .webm 
| AVI | .avi 
| MOV | .mov 



## Erreur probables
- 404 durant l'export : video inexistante ou mauvaise ID
- 400 "Video traitee non disponible" : traiter la video dabord (video/processing)
- 400 "Ne peut exporter que les videos terminees" : attendre la fin du traitement
- FFmpeg error :  Installer ffmpeg et ajouter aux variables systeme
- Celery error : S'assurer que redis est lance

