from django.conf import settings
import random
import os
import boto3


ascii_braille_map = {' ': '⠀', '!': '⠮', '"': '⠐', '#': '⠼', '$': '⠫', '%': '⠩',
                     '&': '⠯', '\'': '⠄', '(': '⠷', ')': '⠾', '*': '⠡', '+': '⠬',
                     ',': '⠠', '-': '⠤', '.': '⠨', '/': '⠌', '0': '⠴', '1': '⠂',
                     '2': '⠆', '3': '⠒', '4': '⠲', '5': '⠢', '6': '⠖', '7': '⠶',
                     '8': '⠦', '9': '⠔', ':': '⠱', ';': '⠰', '<': '⠣', '=': '⠿',
                     '>': '⠜', '?': '⠹', '@': '⠈', 'a': '⠁', 'b': '⠃', 'c': '⠉',
                     'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛', 'h': '⠓', 'i': '⠊',
                     'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝', 'o': '⠕',
                     'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥',
                     'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵', '[': '⠪',
                     '\\': '⠳', ']': '⠻', '^': '⠘', '_': '⠸'}

binary_braille_map = {' ': '000000', '!': '011101', '"': '000010', '#': '001111', '$': '110101', '%': '100101',
                      '&': '111101', '\'': '001000', '(': '111011', ')': '111011', '*': '100001', '+': '001101',
                      ',': '000001', '-': '001001', '.': '000101', '/': '001100', '0': '001011', '1': '010000',
                      '2': '011000', '3': '010010', '4': '010011', '5': '010001', '6': '011010', '7': '011011',
                      '8': '011001', '9': '001010', ':': '100011', ';': '000011', '<': '110001', '=': '111111',
                      '>': '001110', '?': '100111', '@': '000100', 'a': '100000', 'b': '110000', 'c': '100100',
                      'd': '100110', 'e': '100010', 'f': '110100', 'g': '110110', 'h': '110010', 'i': '010100',
                      'j': '010110', 'k': '101000', 'l': '111000', 'm': '101100', 'n': '101110', 'o': '101010',
                      'p': '111100', 'q': '111110', 'r': '111010', 's': '011100', 't': '011110', 'u': '101001',
                      'v': '111001', 'w': '010111', 'x': '101101', 'y': '101111', 'z': '101011', '[': '010101',
                      '\\': '110011', ']': '110111', '^': '000110', '_': '000111'}


class BrailleTranslator:

    def __init__(self, img):
        self.img_name = img.name
        self.img_data = b''
        self.img_path = self.file_loc_helper(img)
        self.conv_str = None
        self.output = None

    def file_loc_helper(self, image_data):
        try:
            img_path = f"{settings.MEDIA_ROOT}/{image_data.name}"
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
        try:
            _lowered_str = self.conv_str.lower()
            res_str = [ascii_braille_map[val] for val in _lowered_str if ascii_braille_map.get(val)]
            self.output = ''.join(res_str)
            return self.output
        except:
            raise Exception("Invalid characters detected in translated text.")

    def convert_to_binary(self):
        try:
            _lowered_str = self.conv_str.lower()
            res_str = [binary_braille_map[val] for val in _lowered_str if binary_braille_map.get(val)]
            self.output = ''.join(res_str)
            return self.output
        except Exception:
            raise Exception("Invalid characters detected in translated text.")

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
        except Exception as e:
            raise Exception(e)


