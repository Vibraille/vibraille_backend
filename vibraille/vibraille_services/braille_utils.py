from django.conf import settings
import cv2
import random
import os
import pytesseract
import boto3


ascii_braille_map = {' ': '⠀', '!': '⠮', '"': '⠐', '#': '⠼', '$': '⠫', '%': '⠩',
                     '&': '⠯', '': '⠄', '(': '⠷', ')': '⠾', '*': '⠡', '+': '⠬',
                     ',': '⠠', '-': '⠤', '.': '⠨', '/': '⠌', '0': '⠴', '1': '⠂',
                     '2': '⠆', '3': '⠒', '4': '⠲', '5': '⠢', '6': '⠖', '7': '⠶',
                     '8': '⠦', '9': '⠔', ':': '⠱', ';': '⠰', '<': '⠣', '=': '⠿',
                     '>': '⠜', '?': '⠹', '@': '⠈', 'a': '⠁', 'b': '⠃', 'c': '⠉',
                     'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊',
                     'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
                     'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥',
                     'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵', '[': '⠪',
                     '\\': '⠳', ']': '⠻', '^': '⠘', '_': '⠸'}


class BrailleTranslator:

    def __init__(self, img):
        self.img_name = img.name
        self.img_data = b''
        self.img_path = self.file_loc_helper(img)
        self.conv_str = None
        self.output = None

    def file_loc_helper(self, image_data):
        try:
            img_path = f"{settings.MEDIA_ROOT}/tmp/{image_data.name}"
            with open(img_path, 'wb+') as destination:
                for chunk in image_data.chunks():
                    destination.write(chunk)
                    self.img_data += chunk
            return img_path
        except Exception as e:
            raise Exception(e)

    def convert_img_to_str(self):
        try:
            textract_complete = False
            client = boto3.client(
                'textract',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            response = client.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Name': self.img_name}},
                ClientRequestToken=str(random.randint(1, 1e10))
            )
            jobid = response['JobId']
            while not textract_complete:
                _curstat = client.get_document_text_detection(JobId=jobid)
                if _curstat.get('JobStatus') == 'SUCCEEDED':
                    textract_complete = True
                elif _curstat.get('JobStatus') == 'FAILED' or _curstat.get('JobStatus') == 'PARTIAL_SUCCESS':
                    raise Exception(_curstat.get("Warnings"))
            response = client.get_document_text_detection(JobId=jobid)
            found_words = [a.get("Text") for a in response.get("Blocks") if a.get("BlockType") == 'LINE' and a.get("Text")]
            self.conv_str = " ".join(found_words)
            return self.conv_str
        except Exception as e:
            raise Exception(e)

    def convert_str_to_braille(self):
        _lowered_str = self.conv_str.lower()
        res_str = [ascii_braille_map[val] for val in _lowered_str if ascii_braille_map.get(val)]
        self.output = ''.join(res_str)
        return self.output

    def upload_to_s3(self):
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        try:
            with open(self.img_path, 'rb') as data:
                s3.upload_fileobj(
                    data,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    self.img_name)
            self._remove_tmp_file()
        except Exception as e:
            raise Exception(e)

    def _remove_tmp_file(self):
        try:
            os.remove(self.img_path)
        except:
            pass


