# TinyTitle 🎭

TinyTitle is a lightweight browser-based supertitle system for live theatre.

It allows an operator to project translated subtitles during a stage play
while controlling cues manually with the keyboard.

## How to use it ?

### 1. Genesis
For every scene, create separate json file in below format, using AI assistant for translation

#### Why this weird format ?
 * Mapping helps our tool to preview and project in language of our choice
 * It give lot of control over dialogue cues
 * This mapping is also AI generated, so no efforts, 
   we just dump the original scenes request our friend GPT / Gemini to generate translation in this format.
```bash
# Original Script:
पाचपोर: या. मस्त खोली आहे. एकट्यासाठी एकदम फस्क्लास.
पाचपोर: तिकडे आत स्वैपाकघर. आणि संडास बाथरूम बाहेर. कॉमन. पण या खोलीला जवळ आहे.
पाचपोर: कशी वाटली जागा?
```
##### Sample format
```json
{
  "scene_index": 1,
  "scene_title": "Anna arrives",
  "location": "Chawl room",
  "notes": "",
  "lines": [
    {
      "line_index": 1,
      "speaker_marathi": "पाचपोर",
      "speaker_english": "Paachpor",
      "marathi": "या. मस्त खोली आहे. एकट्यासाठी एकदम फस्क्लास.",
      "english": "Please come in. This is the room, perfect for a single person."
    },
    {
      "line_index": 2,
      "speaker_marathi": "पाचपोर",
      "speaker_english": "Paachpor",
      "marathi": "तिकडे आत स्वैपाकघर. आणि संडास बाथरूम बाहेर. कॉमन. पण या खोलीला जवळ आहे.",
      "english": "That's the kitchen. Bathrooms are shared outside but close to this room."
    },
    {
      "line_index": 3,
      "speaker_marathi": "पाचपोर",
      "speaker_english": "Paachpor",
      "marathi": "कशी वाटली जागा?",
      "english": "Did you like the place?"
    }
  ]
}
```
```bash
#  We had 13 scenes, created scene-1.json to scene-13.json 
#    translation in above json format 
 Mar 12 01:22 TinyTitle.html
 Mar 12 01:36 bundle_script.py
 Mar 12 01:40 readme.md
 Mar 11 23:11 scene-1.json
 Mar  7 17:42 scene-2.json
 Mar  7 17:50 scene-3.json
 Mar  7 18:07 scene-4.json
 Mar  7 18:19 scene-5.json
 Mar  7 18:29 scene-6.json
 Mar  7 18:32 scene-7.json
 Mar 12 00:03 scene-8.json
 Mar  7 19:00 scene-9.json
 Mar  7 19:06 scene-10.json
 Mar  7 19:12 scene-11.json
 Mar  7 19:23 scene-12.json
 Mar 12 00:03 scene-13.json
```

### 2. Bundle it

* We will bundle all the scenes into a single json file
* --lines denotes number of lines to be displayed on screen
```bash 
python bundle_script.py . --lines 3 --output baaki.json

> 
python3 bundle_script.py . --lines 3 --output baaki.json

Scenes found: ['scene-1.json', 'scene-2.json', 'scene-3.json', 'scene-4.json', 'scene-5.json', 'scene-6.json', 'scene-7.json', 'scene-8.json', 'scene-9.json', 'scene-10.json', 'scene-11.json', 'scene-12.json', 'scene-13.json']
Loaded scene-1.json
Loaded scene-2.json
Loaded scene-3.json
Loaded scene-4.json
Loaded scene-5.json
Loaded scene-6.json
Loaded scene-7.json
Loaded scene-8.json
Loaded scene-9.json
Loaded scene-10.json
Loaded scene-11.json
Loaded scene-12.json
Loaded scene-13.json

Success!
Scenes bundled: 13
Lines per block: 3
Output file: baaki.json

scsapre: TinyTitles % 
```

### 3. Test it

* open TinyTitle.html on chrome / browser
* upload the generated bundled file into it
<img width="718" height="323" alt="image" src="https://github.com/user-attachments/assets/e4574f82-6afa-4678-80dd-57ca3be0613a" />
<img width="1434" height="789" alt="image" src="https://github.com/user-attachments/assets/7558dc8d-b627-4ba0-b5e9-ede11053124a" />


