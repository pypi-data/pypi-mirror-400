#!/usr/bin/env python3
"""
Create Anki .apkg files from card data.

Usage:
    python create_anki_package.py <output_path> [deck_name]

Input: JSON via stdin with structure:
{
    "deck_name": "Cards from Claude",  // optional, defaults to "Cards from Claude"
    "theme": "minimal",                // optional, one of: minimal, rich, bold, ios
    "batch_tags": ["batch-2024-01-15"],  // optional, tags applied to ALL cards
    "cards": [
        {
            "type": "front-back",
            "question": "...",
            "answer": "...",
            "example": "...",      // optional
            "extra_info": "...",   // optional
            "author": "...",       // optional, defaults to "Claude"
            "source": "...",       // optional, defaults to "General Knowledge"
            "source_link": "",     // optional
            "tags": ["tag1"]       // optional, per-card tags (merged with batch_tags)
        },
        {
            "type": "concept",
            "concept": "...",
            "definition": "...",
            "example": "...",      // optional
            "extra_info": "...",   // optional
            "author": "...",       // optional, defaults to "Claude"
            "source": "...",       // optional, defaults to "General Knowledge"
            "source_link": "",     // optional
            "tags": ["tag1"]       // optional
        },
        {
            "type": "cloze",
            "cloze_text": "...",   // text with {{c1::...}} syntax
            "example": "...",      // optional
            "extra_info": "...",   // optional
            "author": "...",       // optional, defaults to "Claude"
            "source": "...",       // optional, defaults to "General Knowledge"
            "source_link": "",     // optional
            "tags": ["tag1"]       // optional
        },
        {
            "type": "image",
            "image_path": "/path/to/image.jpg",  // path to image file
            "prompt": "What building is this?",  // question shown with image
            "answer": "Empire State Building",   // answer revealed on flip
            "extra_info": "...",   // optional
            "author": "...",       // optional, defaults to "Claude"
            "source": "...",       // optional, defaults to "General Knowledge"
            "source_link": "",     // optional
            "tags": ["tag1"]       // optional
        },
        {
            "type": "person",
            "full_name": "Jane Smith",           // required
            "photo_path": "/path/to/photo.jpg",  // optional - generates name recognition card
            "birthday": "March 15",              // optional
            "current_city": "San Francisco",     // optional
            "phone_number": "555-123-4567",      // optional
            "partner_name": "John Smith",        // optional
            "children_names": "Emma, Lucas",     // optional
            "pet_names": "Max (golden retriever)", // optional
            "hobbies": "Rock climbing, pottery", // optional
            "title": "Senior Product Manager",   // optional
            "reports_to": "Sarah Chen",          // optional
            "direct_reports": "Tom, Alice, Bob", // optional
            "company": "Acme Corp",              // optional
            "tags": ["tag1"]                     // optional
        },
        {
            "type": "image-occlusion",
            "image_path": "/path/to/diagram.jpg",    // required
            "header": "Label the heart structures",  // optional
            "back_extra": "Additional context",      // optional
            "occlusion_mode": "hide_all_guess_one",  // or "hide_one_guess_one"
            "occlusions": [                          // required array of occlusion regions
                {
                    "cloze_num": 1,                  // required, 1-indexed
                    "label": "Left Ventricle",       // required, answer text
                    "shape": "ellipse",              // "rect" or "ellipse"
                    "left": 0.35,                    // normalized 0-1, left edge
                    "top": 0.55,                     // normalized 0-1, top edge
                    "width": 0.15,                   // normalized 0-1
                    "height": 0.20,                  // normalized 0-1
                    "fill": "#ffeba2"                // optional, mask color
                }
            ],
            "tags": ["tag1"]                         // optional
        }
    ]
}

Example:
    echo '{"batch_tags": ["linux-kernel"], "cards": [...]}' | python create_anki_package.py output.apkg

Note: This script generates Anki 2.1 format packages (.apkg). All card templates
are designed for and tested with Anki 2.1+. If you need to extract card formats
from existing .apkg files for updating this skill, export them from Anki 2.1.
"""

import sys
import json
import random
import re
import os
import logging
import base64
import mimetypes
from typing import Any, Optional
from pathlib import Path

import genanki
from PIL import Image

# Import theme system
from .themes import (
    THEMES,
    DEFAULT_THEME,
    get_theme_model_id,
    get_theme_model_name,
    get_front_back_css,
    get_concept_css,
    get_cloze_css,
    get_image_css,
    get_person_css,
    get_image_occlusion_css,
)
from .markdown import markdown_to_html, convert_card_fields

# Set up logging
logger = logging.getLogger(__name__)


# Stable model IDs (matching the user's existing note types)
FRONT_BACK_MODEL_ID = 1732590444335
CONCEPT_MODEL_ID = 1734130500288
CLOZE_MODEL_ID = 1761346594645
IMAGE_MODEL_ID = 1735412847293
PERSON_MODEL_ID = 1767049421568
IMAGE_OCCLUSION_MODEL_ID = 1735412847294  # New model for Image Occlusion

# CSS for Front-Back model
FRONT_BACK_CSS = '''html { overflow: scroll; overflow-x: hidden; }

/* GENERAL PAGE STYLING */
body {
    font-family: 'Inter', sans-serif;
    font-size: 18px;
    color: #333;
    background-color: #FFFFFF;
    margin: 0;
    padding: 20px;
}

.card-header {
    font-size: 14px;
    color: #888;
    text-align: left;
    margin-bottom: 20px;
}

.card-header p {
    margin: 0;
}

.question {
    font-weight: bold;
    color: #333;
    font-size: 20px;
    text-align: center;
    margin-bottom: 20px;
}

.answer {
    font-family: 'Georgia', serif;
    font-size: 18px;
    color: #333;
    text-align: left;
    margin-bottom: 20px;
}

.extra-info {
    font-size: 16px;
    color: #555;
    font-style: italic;
    margin-top: 10px;
}

li {
    margin-bottom: 1em;
}

/* DARK MODE */
.night_mode body {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

.night_mode .card-header {
    color: #888;
}

.night_mode .question {
    color: #e0e0e0;
}

.night_mode .answer {
    color: #d0d0d0;
}

.night_mode .extra-info {
    color: #a0a0a0;
}'''

# CSS for Concept model
CONCEPT_CSS = '''/* GENERAL PAGE STYLING */
body {
    font-family: 'Inter', sans-serif;
    font-size: 18px;
    color: #333;
    background-color: #FFFFFF;
    margin: 0;
    padding: 20px;
}

.card-header {
    font-size: 14px;
    color: #888;
    text-align: left;
    margin-bottom: 20px;
}

.card-header p {
    margin: 0;
}

.concept-instruction {
    font-size: 14px;
    color: #555;
    font-style: italic;
    text-align: center;
    margin-bottom: 10px;
}

.question {
    font-weight: bold;
    color: #333;
    font-size: 20px;
    text-align: center;
    margin-bottom: 20px;
}

.answer {
    font-family: 'Georgia', serif;
    font-size: 18px;
    color: #333;
    text-align: left;
    margin-bottom: 20px;
}

.extra-info {
    font-size: 16px;
    color: #555;
    font-style: italic;
    margin-top: 10px;
}

li {
    margin-bottom: 1em;
}

/* DARK MODE */
.night_mode body {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

.night_mode .card-header {
    color: #888;
}

.night_mode .concept-instruction {
    color: #a0a0a0;
}

.night_mode .question {
    color: #e0e0e0;
}

.night_mode .answer {
    color: #d0d0d0;
}

.night_mode .extra-info {
    color: #a0a0a0;
}'''

# CSS for Cloze model (Book Notes: Cloze Deletion)
CLOZE_CSS = '''html { overflow: scroll; overflow-x: hidden; }

/* GENERAL PAGE STYLING */
body {
	font-family: 'Inter', sans-serif;
	font-size: 18px;
	color: #333;
	background-color: #FFFFFF;
	margin: 0;
	padding: 20px;
}

/* TITLE AND AUTHOR */
.card-header {
	font-size: 14px;
	color: #888;
	text-align: left;
	margin-bottom: 20px;
}

.card-header p {
	margin: 0;
}

/* QUESTION TEXT */
.question {
	font-weight: bold;
	color: #333;
	font-size: 20px;
	text-align: center;
	margin-bottom: 20px;
}

/* ANSWER TEXT */
.answer {
	font-family: 'Georgia', serif;
	font-size: 18px;
	color: #333;
	text-align: left;
	margin-bottom: 20px;
}

/* EXTRA INFO TEXT */
.extra-info {
	font-size: 16px;
	color: #555;
	font-style: italic;
	margin-top: 10px;
}

/* Cloze highlight */
.cloze {
	font-weight: bold;
	color: #007acc;
}

li {
    margin-bottom: 1em;
}

/* DARK MODE */
.night_mode body {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

.night_mode .card-header {
    color: #888;
}

.night_mode .question {
    color: #e0e0e0;
}

.night_mode .answer {
    color: #d0d0d0;
}

.night_mode .extra-info {
    color: #a0a0a0;
}

.night_mode .cloze {
    color: #4fc3f7;
}'''

# CSS for Image Recognition model
IMAGE_CSS = '''html { overflow: scroll; overflow-x: hidden; }

/* GENERAL PAGE STYLING */
body {
    font-family: 'Inter', sans-serif;
    font-size: 18px;
    color: #333;
    background-color: #FFFFFF;
    margin: 0;
    padding: 20px;
}

.card-header {
    font-size: 14px;
    color: #888;
    text-align: left;
    margin-bottom: 15px;
}

.card-header p {
    margin: 0;
}

/* PROMPT TEXT - appears above image */
.prompt {
    font-weight: bold;
    color: #333;
    font-size: 20px;
    text-align: center;
    margin-bottom: 15px;
}

/* IMAGE CONTAINER - constrained size for mobile */
.image-container {
    text-align: center;
    margin: 10px 0;
}

.image-container img {
    max-height: 40vh;
    max-width: 100%;
    object-fit: contain;
    display: block;
    margin: 0 auto;
    border-radius: 4px;
}

/* ANSWER TEXT */
.answer {
    font-family: 'Georgia', serif;
    font-size: 20px;
    font-weight: bold;
    color: #333;
    text-align: center;
    margin: 20px 0;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 4px;
}

/* EXTRA INFO TEXT */
.extra-info {
    font-size: 16px;
    color: #555;
    font-style: italic;
    margin-top: 10px;
    text-align: center;
}

li {
    margin-bottom: 1em;
}

/* DARK MODE */
.night_mode body {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

.night_mode .card-header {
    color: #888;
}

.night_mode .prompt {
    color: #e0e0e0;
}

.night_mode .answer {
    color: #e0e0e0;
    background-color: #2d2d2d;
}

.night_mode .extra-info {
    color: #a0a0a0;
}'''

# CSS for People model
PERSON_CSS = '''.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
    padding: 20px;
}

/* Constrain photo size to prevent filling entire screen */
.card img {
    max-width: 300px;
    max-height: 300px;
    width: auto;
    height: auto;
    object-fit: contain;
    margin: 10px auto;
    display: block;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 15px 0;
}

/* DARK MODE */
.night_mode .card {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

.night_mode hr {
    border-top-color: #444;
}'''

# CSS for Image Occlusion model
IMAGE_OCCLUSION_CSS = '''html { overflow: scroll; overflow-x: hidden; }

/* GENERAL PAGE STYLING */
body {
    font-family: 'Inter', sans-serif;
    font-size: 18px;
    color: #333;
    background-color: #FFFFFF;
    margin: 0;
    padding: 20px;
}

/* HEADER */
.io-header {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    text-align: center;
    margin-bottom: 15px;
}

/* IMAGE CONTAINER - holds SVG with embedded image */
.io-container {
    position: relative;
    display: inline-block;
    width: 100%;
    max-width: 100%;
    text-align: center;
}

.io-container svg {
    max-width: 100%;
    max-height: 60vh;
    display: block;
    margin: 0 auto;
}

/* OCCLUSION SHAPES */
.io-mask {
    fill: #ffeba2;
    stroke: #e6d08a;
    stroke-width: 2;
}

.io-mask-active {
    fill: #ff6b6b;
    stroke: #cc5555;
    stroke-width: 3;
}

.io-revealed {
    fill: transparent !important;
    stroke: #4CAF50;
    stroke-width: 3;
    stroke-dasharray: 5,3;
}

.io-mask-hidden {
    display: none;
}

/* ANSWER LABEL */
.io-answer {
    font-size: 22px;
    font-weight: bold;
    color: #333;
    text-align: center;
    margin: 15px 0;
    padding: 10px;
    background-color: #f0f8f0;
    border-radius: 8px;
    border-left: 4px solid #4CAF50;
}

/* CLOZE TEXT - hidden but used for answer detection */
.io-cloze-data {
    display: none;
}

/* BACK EXTRA INFO */
.io-back-extra {
    font-size: 16px;
    color: #555;
    font-style: italic;
    margin-top: 15px;
    text-align: center;
}

/* Cloze styling */
.cloze {
    font-weight: bold;
    color: #4CAF50;
}

/* DARK MODE */
.night_mode body {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

.night_mode .io-header {
    color: #e0e0e0;
}

.night_mode .io-mask {
    fill: #5a5030;
    stroke: #7a6a40;
}

.night_mode .io-mask-active {
    fill: #8b4040;
    stroke: #aa5555;
}

.night_mode .io-revealed {
    stroke: #66bb6a;
}

.night_mode .io-answer {
    background-color: #2a3a2a;
    color: #e0e0e0;
    border-left-color: #66bb6a;
}

.night_mode .io-back-extra {
    color: #a0a0a0;
}

.night_mode .cloze {
    color: #66bb6a;
}'''


def get_front_back_model(theme='minimal'):
    """Create the Front-Back (Q on Front, A on Back) model."""
    model_id = get_theme_model_id(FRONT_BACK_MODEL_ID, theme)
    model_name = get_theme_model_name('Book Notes: Q on Front, A on Back', theme)
    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'Example'},
            {'name': 'Extra Info'},
            {'name': 'Author Name'},
            {'name': 'Source (book, article, etc.)'},
            {'name': 'Source (link)'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>
  <br>
  <div class="question">
    {{Question}}
  </div>''',
                'afmt': '''{{FrontSide}}

  <br>
  <div class="answer">
    {{Answer}}
  </div>

  <div class="extra-info">
    {{Extra Info}}
  </div>
</div>''',
            },
        ],
        css=get_front_back_css(theme),
    )


def get_concept_model(theme='minimal'):
    """Create the Concept (Bidirectional) model."""
    model_id = get_theme_model_id(CONCEPT_MODEL_ID, theme)
    model_name = get_theme_model_name('Book Notes: Concept Definitions (Bidirectional)', theme)
    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Concept'},
            {'name': 'Definition'},
            {'name': 'Example'},
            {'name': 'Extra Info'},
            {'name': 'Author Name'},
            {'name': 'Source (book, article, etc)'},
            {'name': 'Source (link)'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc)}}</p>
    <p>By {{Author Name}}</p>
  </div>
<br>
  <div class="concept-instruction">
    Define the concept
  </div>
  <div class="question">
    {{Concept}}
  </div>''',
                'afmt': '''{{FrontSide}}

  <br>
  <div class="answer">
    {{Definition}}
  </div>

  <div class="extra-info">
    <br>{{Example}}
  </div>

  <div class="extra-info">
    <br>{{Extra Info}}
  </div>
</div>''',
            },
            {
                'name': 'Card 2',
                'qfmt': '''<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc)}}</p>
    <p>By {{Author Name}}</p>
  </div>
<br>
  <div class="concept-instruction">
    Name the concept
  </div>
  <div class="answer">
    {{Definition}}
  </div>''',
                'afmt': '''<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc)}}</p>
    <p>By {{Author Name}}</p>
  </div>
<br>
  <div class="concept-instruction">
    Name the concept
  </div>
  <div class="question">
    {{Concept}}
  </div>
<br>
<br>
  <div class="answer">
    {{Definition}}
  </div>

  <div class="extra-info">
    <br>{{Example}}
  </div>

  <div class="extra-info">
    <br>{{Extra Info}}
  </div>
</div>''',
            },
        ],
        css=get_concept_css(theme),
    )


def get_cloze_model(theme='minimal'):
    """Create the Cloze Deletion model (Book Notes: Cloze Deletion)."""
    model_id = get_theme_model_id(CLOZE_MODEL_ID, theme)
    model_name = get_theme_model_name('Book Notes: Cloze Deletion', theme)
    return genanki.Model(
        model_id,
        model_name,
        model_type=genanki.Model.CLOZE,
        fields=[
            {'name': 'Cloze Question & Answer'},
            {'name': 'Example'},
            {'name': 'Extra Info'},
            {'name': 'Author Name'},
            {'name': 'Source (book, article, etc.)'},
            {'name': 'Source (link)'},
        ],
        templates=[
            {
                'name': 'Cloze',
                'qfmt': '''<div class="card">
  <!-- Title and Author -->
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <br>
  <div class="answer">{{cloze:Cloze Question & Answer}}

  </div>''',
                'afmt': '''<div class="card">
  <!-- Title and Author -->
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <br>
  <div class="answer">
    {{cloze:Cloze Question & Answer}}
  </div>

  <div class="extra-info">
    <br>{{Example}}
  </div>

  <div class="extra-info">
    <br>{{Extra Info}}
  </div>
</div>''',
            },
        ],
        css=get_cloze_css(theme),
    )


def get_image_model(theme='minimal'):
    """Create the Image Recognition model (Book Notes: Image Recognition)."""
    model_id = get_theme_model_id(IMAGE_MODEL_ID, theme)
    model_name = get_theme_model_name('Book Notes: Image Recognition', theme)
    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Image'},
            {'name': 'Prompt'},
            {'name': 'Answer'},
            {'name': 'Extra Info'},
            {'name': 'Author Name'},
            {'name': 'Source (book, article, etc.)'},
            {'name': 'Source (link)'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <div class="prompt">{{Prompt}}</div>

  <div class="image-container">
    {{Image}}
  </div>
</div>''',
                'afmt': '''<div class="card">
  <div class="card-header">
    <p>{{Source (book, article, etc.)}}</p>
    <p>By {{Author Name}}</p>
  </div>

  <div class="prompt">{{Prompt}}</div>

  <div class="answer">{{Answer}}</div>

  <div class="image-container">
    {{Image}}
  </div>

  <div class="extra-info">
    {{Extra Info}}
  </div>
</div>''',
            },
        ],
        css=get_image_css(theme),
    )


def get_person_model(theme='minimal'):
    """
    Create the People model for remembering information about people.

    This model uses conditional templates - cards are only generated for fields
    that have content. One note can generate 0-11 cards depending on which
    fields are populated.

    Model ID: 1767049421568 ("People (updated)")
    """
    model_id = get_theme_model_id(PERSON_MODEL_ID, theme)
    model_name = get_theme_model_name('People (updated)', theme)
    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Full Name'},
            {'name': 'Photo'},
            {'name': 'Birthday'},
            {'name': 'Current City'},
            {'name': 'Phone number'},
            {'name': "Partner's name"},
            {'name': "Children's names"},
            {'name': "Pet's names"},
            {'name': 'Hobbies and Interests'},
            {'name': 'Title or Role'},
            {'name': 'Reports to'},
            {'name': 'Direct Reports'},
            {'name': 'Company'},
        ],
        templates=[
            # Template 0: Location
            {
                'name': 'Location',
                'qfmt': '''{{#Current City}}
<div style='font-family: "Arial"; font-size: 20px;'>Where does {{Full Name}} live?</div>
<hr> 
{{/Current City}}''',
                'afmt': '''{{#Current City}}
<div style='font-family: "Arial"; font-size: 20px;'>Where does {{Full Name}} live?</div>
<hr> 
{{Current City}}
{{/Current City}}''',
            },
            # Template 1: Get name from photo
            {
                'name': 'Get name from photo',
                'qfmt': '''{{#Photo}}
<div style='font-family: "Arial"; font-size: 20px;'>Who is this? 

<br> 
<hr> 

{{Photo}}</div>
{{/Photo}}''',
                'afmt': '''{{#Photo}}
<div style='font-family: "Arial"; font-size: 20px;'>Who is this? 

<br> 
<hr> 

</div>
{{Full Name}}

{{/Photo}}''',
            },
            # Template 2: Identify Title
            {
                'name': 'Identify Title',
                'qfmt': '''{{#Title or Role}}
<div style='font-family: "Arial"; font-size: 20px;'>What is {{Full Name}}'s current role?</div>
<hr>
{{/Title or Role}}''',
                'afmt': '''{{#Title or Role}}
<div style='font-family: "Arial"; font-size: 20px;'>What is {{Full Name}}'s current role?</div>
<hr>
{{Title or Role}}
{{/Title or Role}}''',
            },
            # Template 3: Identify Manager
            {
                'name': 'Identify Manager',
                'qfmt': '''{{#Reports to}}
<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s current manager?</div>
<hr>
{{/Reports to}}''',
                'afmt': '''{{#Reports to}}
<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s current manager?</div>
<hr>
{{Reports to}}
{{/Reports to}}''',
            },
            # Template 4: Identify Direct Reports
            {
                'name': 'Identify Direct Reports',
                'qfmt': '''{{#Direct Reports}}
<div style='font-family: "Arial"; font-size: 20px;'>Who does {{Full Name}} manage?</div>
<hr>
{{/Direct Reports}}''',
                'afmt': '''{{#Direct Reports}}
<div style='font-family: "Arial"; font-size: 20px;'>Who does {{Full Name}} manage?</div>
<hr>
{{Direct Reports}}
{{/Direct Reports}}''',
            },
            # Template 5: Identify Partner
            {
                'name': 'Identify Partner',
                'qfmt': '''{{#Partner's name}}
<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s partner?</div>
<hr>
{{/Partner's name}}''',
                'afmt': '''{{#Partner's name}}
<div style='font-family: "Arial"; font-size: 20px;'>Who is {{Full Name}}'s partner?</div>
<hr>
{{Partner's name}}
{{/Partner's name}}''',
            },
            # Template 6: Identify Hobbies
            {
                'name': 'Identify Hobbies',
                'qfmt': '''{{#Hobbies and Interests}}
<div style='font-family: "Arial"; font-size: 20px;'>What are {{Full Name}}'s hobbies and interests?</div>
<hr>
{{/Hobbies and Interests}}''',
                'afmt': '''{{#Hobbies and Interests}}
<div style='font-family: "Arial"; font-size: 20px;'>What are {{Full Name}}'s hobbies and interests?</div>
<hr>
{{Hobbies and Interests}}
{{/Hobbies and Interests}}''',
            },
            # Template 7: Children's names
            {
                'name': "Children's names",
                'qfmt': '''{{#Children's names}}
<div style='font-family: "Arial"; font-size: 20px;'>What are the names of {{Full Name}}'s children?</div>
<hr>
{{/Children's names}}''',
                'afmt': '''{{#Children's names}}
<div style='font-family: "Arial"; font-size: 20px;'>What are the names of {{Full Name}}'s children?</div>
<hr>
{{Children's names}}
{{/Children's names}}''',
            },
            # Template 8: Pet's names
            {
                'name': "Pet's names",
                'qfmt': '''{{#Pet's names}}
<div style='font-family: "Arial"; font-size: 20px;'>What are the names of {{Full Name}}'s pets?</div>
<hr>
{{/Pet's names}}''',
                'afmt': '''{{#Pet's names}}
<div style='font-family: "Arial"; font-size: 20px;'>What are the names of {{Full Name}}'s pets?</div>
<hr>
{{Pet's names}}
{{/Pet's names}}''',
            },
            # Template 9: Identify phone number
            {
                'name': 'Identify phone number',
                'qfmt': '''{{#Phone number}}
<div style='font-family: "Arial"; font-size: 20px;'>What is {{Full Name}}'s phone number?</div>
<hr>
{{/Phone number}}''',
                'afmt': '''{{#Phone number}}
<div style='font-family: "Arial"; font-size: 20px;'>What is {{Full Name}}'s phone number?</div>
<hr>
{{Phone number}}
{{/Phone number}}''',
            },
            # Template 10: Identify Birthday
            {
                'name': 'Identify Birthday',
                'qfmt': '''{{#Birthday}}
<div style='font-family: "Arial"; font-size: 20px;'>When is {{Full Name}}'s birthday?</div>
<hr>
{{/Birthday}}''',
                'afmt': '''{{#Birthday}}
<div style='font-family: "Arial"; font-size: 20px;'>When is {{Full Name}}'s birthday?</div>
<hr>
{{Birthday}}
{{/Birthday}}''',
            },
            # Template 11: Identify Company
            {
                'name': 'Identify Company',
                'qfmt': '''{{#Company}}
<div style='font-family: "Arial"; font-size: 20px;'>What company does {{Full Name}} work for?</div>
<hr>
{{/Company}}''',
                'afmt': '''{{#Company}}
<div style='font-family: "Arial"; font-size: 20px;'>What company does {{Full Name}} work for?</div>
<hr>
{{Company}}
{{/Company}}''',
            },
        ],
        css=get_person_css(theme),
    )


def get_image_occlusion_model(theme='minimal'):
    """
    Create the Image Occlusion model using SVG-based rendering.

    This model uses a cloze-type note where each occlusion region becomes a separate card.
    SVG overlays are generated in the note fields and toggled via JavaScript.

    Supports two modes:
    - hide_all_guess_one: All regions masked, guess one at a time
    - hide_one_guess_one: Only current region masked

    Model ID: 1735412847294
    """
    model_id = get_theme_model_id(IMAGE_OCCLUSION_MODEL_ID, theme)
    model_name = get_theme_model_name('Image Occlusion (SVG)', theme)
    # JavaScript for toggling classes on SVG masks
    io_script = '''
<script>
(function() {
    var svg = document.querySelector('.io-svg');
    if (!svg) return;

    var mode = svg.getAttribute('data-occlusion-mode') || 'hide_all_guess_one';
    var dataEl = document.getElementById('io-data');
    if (dataEl && dataEl.textContent) {
        try {
            var data = JSON.parse(dataEl.textContent);
            if (data && data.mode) mode = data.mode;
        } catch(e) {
            console.error('Failed to parse occlusion data:', e);
        }
    }

    var masks = svg.querySelectorAll('[data-cloze]');
    if (!masks.length) return;

    var isBack = document.body.classList.contains('io-back') ||
                 document.querySelector('.io-answer') !== null;

    // Find the current cloze number by looking at the rendered cloze text
    var clozeEl = document.getElementById('io-cloze-text');
    var answerEl = document.querySelector('.io-answer');
    var currentCloze = 1;
    var separator = '·';
    var labelOrder = (data && data.regions) ? data.regions.map(function(region) {
        return (region.label || '').trim();
    }) : [];

    function inferFromText(sourceEl) {
        if (!sourceEl) return null;
        var text = (sourceEl.textContent || '').trim();
        if (!text) return null;
        var parts = text.split(separator).map(function(part) {
            return part.trim();
        }).filter(Boolean);
        var blankIndex = parts.findIndex(function(part) {
            return part.indexOf('[...]') !== -1 || part.indexOf('...') !== -1;
        });
        if (blankIndex !== -1) return blankIndex + 1;
        var clozeSpan = sourceEl.querySelector('.cloze');
        if (clozeSpan && labelOrder.length) {
            var label = clozeSpan.textContent.trim();
            var labelIndex = labelOrder.findIndex(function(item) {
                return item === label;
            });
            if (labelIndex !== -1) return labelIndex + 1;
        }
        return null;
    }

    currentCloze = inferFromText(clozeEl) || inferFromText(answerEl) || currentCloze;

    masks.forEach(function(mask) {
        var clozeValue = parseInt(mask.getAttribute('data-cloze'), 10) || 1;
        var isCurrent = clozeValue === currentCloze;
        var shouldShow = false;

        mask.classList.remove('io-mask-active', 'io-revealed', 'io-mask-hidden');

        if (isBack) {
            if (isCurrent) {
                shouldShow = true;
                mask.classList.add('io-revealed');
            } else if (mode === 'hide_all_guess_one') {
                shouldShow = true;
            }
        } else {
            if (mode === 'hide_all_guess_one') {
                shouldShow = true;
                if (isCurrent) {
                    mask.classList.add('io-mask-active');
                }
            } else {
                if (isCurrent) {
                    shouldShow = true;
                    mask.classList.add('io-mask-active');
                }
            }
        }

        if (!shouldShow) {
            mask.classList.add('io-mask-hidden');
        }
    });
})();
</script>
'''

    return genanki.Model(
        model_id,
        model_name,
        model_type=genanki.Model.CLOZE,
        fields=[
            {'name': 'ImageSVG'},
            {'name': 'Occlusions'},
            {'name': 'OcclusionData'},
            {'name': 'Header'},
            {'name': 'BackExtra'},
        ],
        templates=[
            {
                'name': 'Image Occlusion',
                'qfmt': '''<div class="io-card">
{{#Header}}<div class="io-header">{{Header}}</div>{{/Header}}

<div class="io-container">
    {{ImageSVG}}
</div>

<div id="io-cloze-text" class="io-cloze-data">{{cloze:Occlusions}}</div>
<div id="io-data" style="display:none;">{{OcclusionData}}</div>
</div>
''' + io_script,
                'afmt': '''<div class="io-card io-back">
{{#Header}}<div class="io-header">{{Header}}</div>{{/Header}}

<div class="io-container">
    {{ImageSVG}}
</div>

<div class="io-answer">{{cloze:Occlusions}}</div>

{{#BackExtra}}<div class="io-back-extra">{{BackExtra}}</div>{{/BackExtra}}

<div id="io-cloze-text" class="io-cloze-data">{{cloze:Occlusions}}</div>
<div id="io-data" style="display:none;">{{OcclusionData}}</div>
</div>
''' + io_script,
            },
        ],
        css=get_image_occlusion_css(theme),
    )


def _guess_image_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type
    ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    mime_map = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'svg': 'image/svg+xml',
    }
    return mime_map.get(ext, 'application/octet-stream')


def _file_to_base64_data_url(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'rb') as handle:
            data = handle.read()
    except (OSError, IOError) as exc:
        logger.warning(f"Unable to read image file for embedding: {file_path} ({exc})")
        return None

    mime_type = _guess_image_mime_type(file_path)
    encoded = base64.b64encode(data).decode('utf-8')
    return f"data:{mime_type};base64,{encoded}"


def _get_dimensions_from_base64(data_url: str) -> tuple[int, int]:
    """Extract image dimensions from a base64 data URL.

    Returns (width, height) or (0, 0) if extraction fails.
    """
    try:
        # Parse data URL: data:image/png;base64,AAAA...
        if not data_url.startswith('data:'):
            return (0, 0)
        # Extract base64 portion after the comma
        comma_idx = data_url.find(',')
        if comma_idx == -1:
            return (0, 0)
        b64_data = data_url[comma_idx + 1:]
        image_bytes = base64.b64decode(b64_data)
        # Use PIL to get dimensions
        import io
        with Image.open(io.BytesIO(image_bytes)) as img:
            return img.size
    except Exception:
        return (0, 0)


def create_front_back_note(card_data, model, batch_tags=None):
    """Create a Front-Back note from card data."""
    # Convert markdown to HTML
    converted = convert_card_fields(card_data)
    
    tags = converted.get('tags', [])
    if batch_tags:
        tags = list(set(tags + batch_tags))  # Merge and dedupe
    return genanki.Note(
        model=model,
        fields=[
            converted.get('question', ''),
            converted.get('answer', ''),
            converted.get('example', ''),
            converted.get('extra_info', ''),
            converted.get('author', 'Claude'),
            converted.get('source', 'General Knowledge'),
            converted.get('source_link', ''),
        ],
        tags=tags
    )


def create_concept_note(card_data, model, batch_tags=None):
    """Create a Concept note from card data."""
    # Convert markdown to HTML
    converted = convert_card_fields(card_data)
    
    tags = converted.get('tags', [])
    if batch_tags:
        tags = list(set(tags + batch_tags))  # Merge and dedupe
    return genanki.Note(
        model=model,
        fields=[
            converted.get('concept', ''),
            converted.get('definition', ''),
            converted.get('example', ''),
            converted.get('extra_info', ''),
            converted.get('author', 'Claude'),
            converted.get('source', 'General Knowledge'),
            converted.get('source_link', ''),
        ],
        tags=tags
    )


def create_cloze_note(card_data, model, batch_tags=None):
    """Create a Cloze note from card data."""
    # Convert markdown to HTML
    converted = convert_card_fields(card_data)
    
    tags = converted.get('tags', [])
    if batch_tags:
        tags = list(set(tags + batch_tags))  # Merge and dedupe
    return genanki.Note(
        model=model,
        fields=[
            converted.get('cloze_text', ''),
            converted.get('example', ''),
            converted.get('extra_info', ''),
            converted.get('author', 'Claude'),
            converted.get('source', 'General Knowledge'),
            converted.get('source_link', ''),
        ],
        tags=tags
    )


def create_image_note(card_data, model, batch_tags=None):
    """Create an Image Recognition note from card data."""
    # Convert markdown to HTML
    converted = convert_card_fields(card_data)
    
    # Get the image filename from the path
    image_path = converted.get('image_path', '')
    if image_path:
        image_filename = os.path.basename(image_path)
        # Create the Anki image reference
        image_field = f'<img src="{image_filename}">'
    else:
        image_field = ''
    
    tags = converted.get('tags', [])
    if batch_tags:
        tags = list(set(tags + batch_tags))  # Merge and dedupe
    return genanki.Note(
        model=model,
        fields=[
            image_field,
            converted.get('prompt', ''),
            converted.get('answer', ''),
            converted.get('extra_info', ''),
            converted.get('author', 'Claude'),
            converted.get('source', 'General Knowledge'),
            converted.get('source_link', ''),
        ],
        tags=tags
    )


def create_person_note(card_data, model, batch_tags=None):
    """
    Create a Person note from card data.
    
    Unlike other note types, Person notes can generate multiple cards from a single note.
    Cards are only generated for fields that have content (using Anki's conditional templates).
    """
    # Convert markdown to HTML for relevant fields
    converted = convert_card_fields(card_data)
    
    # Get the photo filename from the path if provided
    photo_path = converted.get('photo_path', '')
    if photo_path:
        photo_filename = os.path.basename(photo_path)
        photo_field = f'<img src="{photo_filename}">'
    else:
        photo_field = ''
    
    tags = converted.get('tags', [])
    if batch_tags:
        tags = list(set(tags + batch_tags))  # Merge and dedupe
    
    # Field order must match the model definition exactly:
    # Full Name, Photo, Birthday, Current City, Phone number, Partner's name,
    # Children's names, Pet's names, Hobbies and Interests, Title or Role,
    # Reports to, Direct Reports, Company
    return genanki.Note(
        model=model,
        fields=[
            converted.get('full_name', ''),
            photo_field,
            converted.get('birthday', ''),
            converted.get('current_city', ''),
            converted.get('phone_number', ''),
            converted.get('partner_name', ''),
            converted.get('children_names', ''),
            converted.get('pet_names', ''),
            converted.get('hobbies', ''),
            converted.get('title', ''),
            converted.get('reports_to', ''),
            converted.get('direct_reports', ''),
            converted.get('company', ''),
        ],
        tags=tags
    )


def create_image_occlusion_note(card_data, model, batch_tags=None):
    """
    Create an Image Occlusion note from card data.

    This generates one card per occlusion region (using cloze deletion).
    The occlusions are stored as cloze text with labels, and the SVG masks
    are embedded directly in the note field.

    Accepts either:
    - image_path: path to an image file (preferred, will be read and encoded)
    - image_data: pre-encoded base64 data URL (fallback if file unavailable)

    If using image_data, also provide image_width and image_height for proper
    aspect ratio. If not provided, dimensions will be extracted from the base64.
    """
    image_path = card_data.get('image_path', '')
    image_data_provided = card_data.get('image_data', '')

    # Determine image dimensions for viewbox aspect ratio
    # Priority: 1) explicit width/height, 2) read from file, 3) extract from base64
    viewbox_width = 100.0
    viewbox_height = 100.0
    image_width = card_data.get('image_width', 0)
    image_height = card_data.get('image_height', 0)

    # Try to get dimensions from file if not explicitly provided
    if not (image_width and image_height) and image_path and os.path.exists(image_path):
        try:
            with Image.open(image_path) as img:
                image_width, image_height = img.size
        except (OSError, IOError):
            pass

    # Try to get dimensions from base64 data if still not available
    if not (image_width and image_height) and image_data_provided:
        image_width, image_height = _get_dimensions_from_base64(image_data_provided)

    # Calculate viewbox aspect ratio
    if image_width > 0:
        viewbox_height = viewbox_width * (image_height / image_width)

    viewbox_width_str = f"{viewbox_width:.4f}".rstrip('0').rstrip('.')
    viewbox_height_str = f"{viewbox_height:.4f}".rstrip('0').rstrip('.')

    # Determine image data URL
    # Priority: 1) read from file path, 2) use provided base64 data
    image_data_url = None

    # Try 1: Read from file path if it exists
    if image_path and os.path.exists(image_path):
        image_data_url = _file_to_base64_data_url(image_path)
        if image_data_url is None:
            logger.warning(f"Failed to read image file: {image_path}")

    # Try 2: Use pre-encoded image_data if file read failed or unavailable
    if image_data_url is None and image_data_provided:
        image_data_url = image_data_provided
        logger.debug(f"Using provided image_data (base64) for image-occlusion card")

    # Fail loudly if neither source provided usable image data
    if image_data_url is None:
        path_info = f"image_path={image_path!r}" if image_path else "no image_path"
        data_info = "image_data provided" if image_data_provided else "no image_data"
        raise ValidationError(
            f"Image occlusion card: could not load image. "
            f"Provide either a valid image_path pointing to an existing file, "
            f"or pre-encoded image_data (base64 data URL). "
            f"Got: {path_info}, {data_info}"
        )

    # Build the image tag
    image_tag = (
        f'<image href="{image_data_url}" xlink:href="{image_data_url}" '
        f'x="0" y="0" width="{viewbox_width_str}" height="{viewbox_height_str}" '
        'preserveAspectRatio="xMidYMid meet" />'
    )

    # Build the cloze text from occlusions
    occlusions = card_data.get('occlusions', [])
    cloze_parts = []
    for occ in occlusions:
        cloze_num = occ.get('cloze_num', 1)
        label = occ.get('label', f'Region {cloze_num}')
        cloze_parts.append(f'{{{{c{cloze_num}::{label}}}}}')
    cloze_text = ' · '.join(cloze_parts)

    # Build the occlusion data JSON
    occlusion_mode = card_data.get('occlusion_mode', 'hide_all_guess_one')
    occlusion_data = {
        'mode': occlusion_mode,
        'regions': []
    }
    mask_parts = []
    for occ in occlusions:
        cloze_num = occ.get('cloze_num', 1)
        shape_type = occ.get('shape', 'rect')
        region = {
            'cloze_num': cloze_num,
            'label': occ.get('label', f'Region {cloze_num}'),
            'shape': shape_type,
            'left': occ.get('left', 0),
            'top': occ.get('top', 0),
            'width': occ.get('width', 0.1),
            'height': occ.get('height', 0.1),
        }
        if 'fill' in occ:
            region['fill'] = occ['fill']
        occlusion_data['regions'].append(region)

        left = region['left'] * viewbox_width
        top = region['top'] * viewbox_height
        width = region['width'] * viewbox_width
        height = region['height'] * viewbox_height
        fill_attr = f' style="fill: {region["fill"]};"' if 'fill' in region else ''
        if shape_type == 'ellipse':
            mask_parts.append(
                f'<ellipse class="io-mask" data-cloze="{cloze_num}" '
                f'cx="{left + width / 2:.4f}" cy="{top + height / 2:.4f}" '
                f'rx="{width / 2:.4f}" ry="{height / 2:.4f}"{fill_attr} />'
            )
        else:
            mask_parts.append(
                f'<rect class="io-mask" data-cloze="{cloze_num}" '
                f'x="{left:.4f}" y="{top:.4f}" width="{width:.4f}" '
                f'height="{height:.4f}"{fill_attr} />'
            )

    image_svg = (
        f'<svg class="io-svg" viewBox="0 0 {viewbox_width_str} {viewbox_height_str}" '
        f'preserveAspectRatio="xMidYMid meet" data-occlusion-mode="{occlusion_mode}" '
        'xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">'
        f'{image_tag}'
        f'{"".join(mask_parts)}'
        '</svg>'
    )

    occlusion_data_json = json.dumps(occlusion_data)

    tags = card_data.get('tags', [])
    if batch_tags:
        tags = list(set(tags + batch_tags))

    return genanki.Note(
        model=model,
        fields=[
            image_svg,
            cloze_text,
            occlusion_data_json,
            card_data.get('header', ''),
            card_data.get('back_extra', ''),
        ],
        tags=tags
    )


def count_cloze_deletions(cloze_text: str) -> int:
    """Count the number of cloze deletions in a cloze text."""
    import re
    # Match {{c1::...}}, {{c2::...}}, etc.
    matches = re.findall(r'\{\{c(\d+)::', cloze_text)
    if not matches:
        return 0
    # Return the count of unique cloze numbers
    return len(set(matches))


def count_person_cards(card_data: dict) -> int:
    """
    Count how many cards a person note will generate.
    Cards are generated for each non-empty optional field.
    """
    # Map of JSON field names to whether they generate a card
    card_generating_fields = [
        'photo_path',      # Get name from photo
        'current_city',    # Location
        'title',           # Identify Title
        'reports_to',      # Identify Manager
        'direct_reports',  # Identify Direct Reports
        'partner_name',    # Identify Partner
        'hobbies',         # Identify Hobbies
        'children_names',  # Children's names
        'pet_names',       # Pet's names
        'phone_number',    # Identify phone number
        'birthday',        # Identify Birthday
        'company',         # Identify Company
    ]
    
    count = 0
    for field in card_generating_fields:
        if card_data.get(field):
            count += 1
    return count


class ValidationError(Exception):
    """Raised when input data fails validation."""
    pass


def validate_card(card: Any, index: int) -> None:
    """Validate a single card's structure. Raises ValidationError if invalid."""
    if not isinstance(card, dict):
        raise ValidationError(f"Card {index}: must be a dictionary, got {type(card).__name__}")

    card_type = card.get('type', '').lower()
    if not card_type:
        raise ValidationError(f"Card {index}: missing required 'type' field")

    valid_types = ['front-back', 'concept', 'cloze', 'image', 'person', 'image-occlusion']
    if card_type not in valid_types:
        raise ValidationError(f"Card {index}: invalid type '{card_type}'. Must be one of: {', '.join(valid_types)}")

    # Type-specific required field validation
    required_fields = {
        'front-back': ['question', 'answer'],
        'concept': ['concept', 'definition'],
        'cloze': ['cloze_text'],
        'image': ['image_path', 'prompt', 'answer'],
        'person': ['full_name'],
        'image-occlusion': ['occlusions'],  # image_path OR image_data validated below
    }

    for field in required_fields.get(card_type, []):
        if not card.get(field):
            raise ValidationError(f"Card {index} ({card_type}): missing required field '{field}'")

    # Image-occlusion requires either image_path or image_data
    if card_type == 'image-occlusion':
        has_image_path = bool(card.get('image_path'))
        has_image_data = bool(card.get('image_data'))
        if not has_image_path and not has_image_data:
            raise ValidationError(
                f"Card {index} (image-occlusion): requires either 'image_path' or 'image_data'"
            )

    # Validate cloze syntax
    if card_type == 'cloze':
        cloze_text = card.get('cloze_text', '')
        if '{{c' not in cloze_text or '::' not in cloze_text:
            raise ValidationError(f"Card {index} (cloze): cloze_text must contain cloze syntax like {{{{c1::answer}}}}")

    # Validate occlusions array
    if card_type == 'image-occlusion':
        occlusions = card.get('occlusions', [])
        if not isinstance(occlusions, list) or len(occlusions) == 0:
            raise ValidationError(f"Card {index} (image-occlusion): occlusions must be a non-empty array")


def validate_data(data: Any) -> None:
    """Validate the input data structure. Raises ValidationError if invalid."""
    if not isinstance(data, dict):
        raise ValidationError(f"Input must be a dictionary, got {type(data).__name__}")

    cards = data.get('cards')
    if cards is not None and not isinstance(cards, list):
        raise ValidationError(f"'cards' must be an array, got {type(cards).__name__}")

    batch_tags = data.get('batch_tags')
    if batch_tags is not None and not isinstance(batch_tags, list):
        raise ValidationError(f"'batch_tags' must be an array, got {type(batch_tags).__name__}")

    # Validate each card
    for i, card in enumerate(cards or []):
        validate_card(card, i)


def _resolve_media_path(path_value: str, base_path: Optional[str]) -> str:
    if not path_value or not base_path:
        return path_value

    path = Path(path_value)
    if path.is_absolute():
        return str(path)

    return str(Path(base_path) / path)


def _resolve_card_media_paths(card: dict, base_path: Optional[str]) -> dict:
    if not base_path:
        return card

    resolved = dict(card)
    if "image_path" in resolved:
        resolved["image_path"] = _resolve_media_path(resolved.get("image_path", ""), base_path)
    if "photo_path" in resolved:
        resolved["photo_path"] = _resolve_media_path(resolved.get("photo_path", ""), base_path)
    return resolved


def create_package(data: dict, output_path: str, base_path: Optional[str] = None) -> dict:
    """
    Create an Anki package from the provided data.

    Args:
        data: Dictionary containing deck_name, cards, batch_tags, and theme.
        output_path: File path for the output .apkg file.
        base_path: Base directory to resolve relative media paths.

    Returns:
        Dictionary with statistics about the created package.

    Raises:
        ValidationError: If the input data structure is invalid.
    """
    # Validate input data
    validate_data(data)

    deck_name = data.get('deck_name', 'Cards from Claude')
    cards = data.get('cards', [])
    batch_tags = data.get('batch_tags', [])  # Tags applied to all cards in batch
    theme = data.get('theme', DEFAULT_THEME)  # Visual theme for cards

    # Validate theme
    if theme not in THEMES:
        logger.warning(f"Unknown theme '{theme}', using '{DEFAULT_THEME}'")
        theme = DEFAULT_THEME

    # Create deck with random ID
    deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        deck_name
    )

    # Get models with theme
    front_back_model = get_front_back_model(theme)
    concept_model = get_concept_model(theme)
    cloze_model = get_cloze_model(theme)
    image_model = get_image_model(theme)
    person_model = get_person_model(theme)
    image_occlusion_model = get_image_occlusion_model(theme)

    # Track counts
    fb_count = 0
    concept_count = 0
    cloze_count = 0
    image_count = 0
    person_count = 0
    image_occlusion_count = 0
    total_cloze_cards = 0
    total_person_cards = 0
    total_io_cards = 0
    
    # Collect media files for image and person cards
    media_files = []
    
    # Add notes
    for card in cards:
        resolved_card = _resolve_card_media_paths(card, base_path)
        card_type = resolved_card.get('type', '').lower()
        
        if card_type == 'front-back':
            note = create_front_back_note(resolved_card, front_back_model, batch_tags)
            deck.add_note(note)
            fb_count += 1
        elif card_type == 'concept':
            note = create_concept_note(resolved_card, concept_model, batch_tags)
            deck.add_note(note)
            concept_count += 1
        elif card_type == 'cloze':
            note = create_cloze_note(resolved_card, cloze_model, batch_tags)
            deck.add_note(note)
            cloze_count += 1
            total_cloze_cards += count_cloze_deletions(resolved_card.get('cloze_text', ''))
        elif card_type == 'image':
            note = create_image_note(resolved_card, image_model, batch_tags)
            deck.add_note(note)
            image_count += 1
            # Track the media file
            image_path = resolved_card.get('image_path', '')
            if image_path and os.path.exists(image_path):
                media_files.append(image_path)
            elif image_path:
                logger.warning(f"Image file not found: {image_path}")
        elif card_type == 'person':
            note = create_person_note(resolved_card, person_model, batch_tags)
            deck.add_note(note)
            person_count += 1
            total_person_cards += count_person_cards(resolved_card)
            # Track the photo file if provided
            photo_path = resolved_card.get('photo_path', '')
            if photo_path and os.path.exists(photo_path):
                media_files.append(photo_path)
            elif photo_path:
                logger.warning(f"Photo file not found: {photo_path}")
        elif card_type == 'image-occlusion':
            note = create_image_occlusion_note(resolved_card, image_occlusion_model, batch_tags)
            deck.add_note(note)
            image_occlusion_count += 1
            # Count cards based on number of occlusions
            occlusions = resolved_card.get('occlusions', [])
            total_io_cards += len(occlusions)
            # Track the image file
            image_path = resolved_card.get('image_path', '')
            if image_path and os.path.exists(image_path):
                media_files.append(image_path)
            elif image_path:
                logger.warning(f"Image file not found: {image_path}")
        else:
            logger.warning(f"Unknown card type '{card_type}', skipping")
    
    # Create and save package with media files
    package = genanki.Package(deck)
    if media_files:
        package.media_files = media_files
    package.write_to_file(output_path)
    
    return {
        'deck_name': deck_name,
        'output_path': output_path,
        'theme': theme,
        'front_back_count': fb_count,
        'concept_count': concept_count,
        'cloze_count': cloze_count,
        'image_count': image_count,
        'person_count': person_count,
        'image_occlusion_count': image_occlusion_count,
        'total_notes': fb_count + concept_count + cloze_count + image_count + person_count + image_occlusion_count,
        # Front-Back = 1 card, Concept = 2 cards (bidirectional), Cloze = N cards per deletion,
        # Image = 1 card, Person = N cards based on filled fields, Image Occlusion = N cards per occlusion
        'total_cards': fb_count + (concept_count * 2) + total_cloze_cards + image_count + total_person_cards + total_io_cards,
        'media_files_included': len(media_files)
    }


def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python create_anki_package.py <output_path> [deck_name]")
        logger.error("Input JSON via stdin")
        sys.exit(1)
    
    output_path = sys.argv[1]
    cli_deck_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Read JSON from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        sys.exit(1)
    
    # CLI deck name overrides JSON
    if cli_deck_name:
        data['deck_name'] = cli_deck_name
    
    # Create the package
    result = create_package(data, output_path)
    
    # Output result as JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
