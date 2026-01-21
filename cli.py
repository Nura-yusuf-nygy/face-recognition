#!/usr/bin/env python3
"""
CLI utility for face recognition operations.
Provides command-line interface for common tasks.
"""
import argparse
import os
from app.face_recognizer import FaceRecognizer


def main():
    parser = argparse.ArgumentParser(
        description='Face Recognition CLI - Command-line interface for face recognition'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Recognize command
    recognize_parser = subparsers.add_parser('recognize', help='Recognize faces in image')
    recognize_parser.add_argument('image', help='Path to image file')
    recognize_parser.add_argument('--tolerance', type=float, default=0.6, help='Face comparison tolerance')
    recognize_parser.add_argument('--model', default='hog', choices=['hog', 'cnn'], help='Detection model')

    # Add face command
    add_parser = subparsers.add_parser('add', help='Add face to known faces')
    add_parser.add_argument('image', help='Path to image file')
    add_parser.add_argument('name', help='Person name')
    add_parser.add_argument('--model', default='hog', choices=['hog', 'cnn'], help='Detection model')

    # List command
    list_parser = subparsers.add_parser('list', help='List known faces')

    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode all known faces')
    encode_parser.add_argument('--tolerance', type=float, default=0.6, help='Face comparison tolerance')
    encode_parser.add_argument('--model', default='hog', choices=['hog', 'cnn'], help='Detection model')

    args = parser.parse_args()

    if args.command == 'recognize':
        recognize_image(args)
    elif args.command == 'add':
        add_face(args)
    elif args.command == 'list':
        list_known_faces()
    elif args.command == 'encode':
        encode_known_faces(args)
    else:
        parser.print_help()


def recognize_image(args):
    """Recognize faces in an image."""
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        return

    print(f"Loading recognizer (tolerance={args.tolerance}, model={args.model})...")
    recognizer = FaceRecognizer(tolerance=args.tolerance, model=args.model)
    recognizer.load_known_faces()

    print(f"Recognizing faces in: {args.image}")
    result = recognizer.recognize_faces_in_image(args.image)

    if result['error']:
        print(f"Error: {result['error']}")
        return

    faces = result['faces']
    print(f"\nFound {len(faces)} face(s):")
    print("-" * 50)

    for i, face in enumerate(faces, 1):
        print(f"\nFace {i}:")
        print(f"  Name: {face['name']}")
        print(f"  Confidence: {face['confidence']:.4f}")
        loc = face['location']
        print(f"  Location: ({loc['left']}, {loc['top']}, {loc['right']}, {loc['bottom']})")


def add_face(args):
    """Add a face to known faces."""
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        return

    print(f"Adding face for: {args.name}")
    print(f"Image: {args.image}")

    recognizer = FaceRecognizer(model=args.model)
    result = recognizer.add_face_to_known(args.image, args.name)

    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")


def list_known_faces():
    """List all known faces."""
    known_faces_dir = 'known_faces'

    if not os.path.exists(known_faces_dir):
        print("No known faces directory found.")
        return

    faces = []
    for person_name in os.listdir(known_faces_dir):
        person_path = os.path.join(known_faces_dir, person_name)
        if os.path.isdir(person_path):
            image_count = len([f for f in os.listdir(person_path)
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))])
            faces.append((person_name, image_count))

    if not faces:
        print("No known faces found.")
        return

    print("Known Faces:")
    print("-" * 50)
    for name, count in sorted(faces):
        print(f"  {name}: {count} image(s)")
    print("-" * 50)
    print(f"Total: {len(faces)} person(s)")


def encode_known_faces(args):
    """Encode all known faces."""
    print(f"Loading and encoding known faces (model={args.model})...")
    recognizer = FaceRecognizer(tolerance=args.tolerance, model=args.model)
    recognizer.load_known_faces()

    print(f"\n✓ Successfully encoded {len(recognizer.known_face_encodings)} face(s)")
    print(f"  Known people: {len(set(recognizer.known_face_names))}")


if __name__ == '__main__':
    main()
