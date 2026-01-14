import math
from datetime import datetime
from pytz import timezone
from PIL import ImageFont
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfWriter, PdfReader

from .PaperlogicSign.paperlogic_signature.pdf_utils.reader import PdfFileReader


def _get_page_dimensions(pdf_path, pdf_pwd, page_ix=0):
    with open(pdf_path, 'rb') as f:
        reader = PdfFileReader(f, strict=False)
        
        if reader.security_handler and pdf_pwd:
            reader.security_handler.authenticate(pdf_pwd.encode('utf-8'))
        
        total_pages = int(reader.root['/Pages']['/Count'])

        if page_ix < 0 or page_ix >= total_pages:
            page_ix = 0

        page_ref, _ = reader.find_page_for_modification(page_ix)
        page_obj = page_ref.get_object()
        
        pagetree_obj = page_obj
        while True:
            try:
                mb = pagetree_obj['/MediaBox']
                break
            except KeyError:
                try:
                    pagetree_obj = pagetree_obj['/Parent']
                except KeyError:
                    raise ValueError(f'Page {page_ix} does not have a /MediaBox')
        
        x1, y1, x2, y2 = [float(v) for v in mb]
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return width, height, total_pages


def cal_sign_location(pageWidth):
    print('cal_sign_location')
    try:
        allUser = 1
        signing_no = 1

        signing_positon_no = signing_no - 1

        space = 4
        imprintSize = 60

        pageWidth = pageWidth - (space * 2)

        imprintPerRow = math.floor((pageWidth + space) / (imprintSize + space))
        if allUser < imprintPerRow:
            imprintPerRow = allUser

        allImprintRowWidth = (imprintPerRow * (imprintSize + space)) - space
        remainingSpace = pageWidth - allImprintRowWidth
        margin = remainingSpace / 2

        left = space + margin

        row_sign = 1
        if imprintPerRow >= signing_no:
            row_sign
        else:
            row_sign = math.ceil(signing_no/imprintPerRow)

        L = left + (signing_positon_no*(imprintSize+space))

        if (row_sign > 1):
            L = left + ((signing_positon_no %
                        imprintPerRow)*(imprintSize+space))

        B = (row_sign*space)+((row_sign-1)*imprintSize)
        LW = L+imprintSize
        BH = B+imprintSize

        return {
            'message': 'success',
            'L': L,
            'B': B,
            'LW': LW,
            'BH': BH
        }

    except Exception as ex:
        response = {
            'message': str(ex),
            'error': 'cal-sign_loc-error'
        }

        return response

def text_wrap(text, font, max_width, max_lines=None):
    """Wrap text based on specified width.
    This is to enable text of width more than the image width to be displayed
    nicely.
    @params:
        text: str
            text to wrap
        font: obj
            font of the text
        max_width: int
            width to split the text with
        max_lines: int, optional
            maximum number of lines to wrap
    @return
        lines: list[str]
            list of sub-strings
    """
    lines = []

    # If the text width is smaller than the image width, then no need to split
    # just add it to the line list and return
    if font.getlength(text) <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than the image width
        while i < len(words) and (max_lines is None or len(lines) < max_lines):
            line = ''
            while i < len(words) and font.getlength(line + words[i]) <= max_width:
                line = line + words[i] + " "
                i += 1
            if line:
                lines.append(line.strip())
            if not line:
                str_words = words[i]
                n = max_width
                ct = len(line + str_words)
                str_width = font.getlength(line + str_words)
                one_char_width = (str_width / ct)
                total_char_per_line = math.floor(n / one_char_width)
                w = total_char_per_line
                ic = 0
                while ic < ct and (max_lines is None or len(lines) < max_lines):
                    if ic + w < len(str_words):
                        line = str_words[ic:ic + w]
                        lines.append(line)
                    else:
                        line = str_words[ic:len(str_words)]
                        lines.append(line)
                    ic += w
                i += 1

            if max_lines is not None and len(lines) >= max_lines:
                if i < len(words):
                    lines[-1] += "..."
                break
            print("text wrap 4")
            '''
            if font.getlength(line + words[i]) <= max_width:
                line = line + words[i]+ " "
                i += 1
                lines.append(line)
            else:
                str_words = words[i]
                n = max_width
                ct = len(line + str_words)
                str_width = font.getlength(line + str_words)
                one_char_width = (str_width/ct)
                total_char_per_line = math.floor(n/one_char_width)
                w = total_char_per_line
                ic = 0
                while ic < ct:
                    if ic+w < len(str_words):
                        lines.append(str_words[ic:ic+w])
                    else:
                        lines.append(str_words[ic:len(str_words)])
                    ic += w
                i += 1
            '''
            # while i < len(words) and font.getlength(line + words[i])[0] <= max_width:
            #    line = line + words[i]+ " "
            #    i += 1
            # if not line:
            #    line = words[i]
            #    i += 1
            # lines.append(line)
    # Ensure only up to max_lines are returned if max_lines is specified
    return lines[:max_lines] if max_lines is not None else lines

def create_vis_file(local_imprint_folder, local_tmp_folder, user_info, certificate_type_id):

    # user_full_name, user_company_name, user_id, certificate_type_id
    # group_custom_label, self_certificate


    try:
        # today = date.today().isoformat()
        Tk = timezone('Asia/Tokyo')
        loc_dt  = datetime.now()
        tk_dt = loc_dt.astimezone(Tk)
        today = str(tk_dt).split(' ')[0]

        # s3ul = boto3.client('s3')
        # s3 = boto3.resource('s3')

        # variable parameter
        # name = data_dict['full_name']
        # name = data_dict['division']
        name = user_info['user_full_name']
        if certificate_type_id == 2:
            if 'group_custom_label' in user_info and user_info['group_custom_label'] != '' and user_info['group_custom_label'] is not None:
                name = user_info['group_custom_label']
            # else:s
            #     name = data_dict['user_full_name']

        # check group custom label...
        # group_custom_label = data_dict['group_custom_label']
        # if group_custom_label != '':
        #     name = group_custom_label

        # company = data_dict['Company_name']
        company = user_info['user_company_name']
        if company and company == 'null':
            company = ''
            
        usr_id = user_info['user_id']

        # 0 = use paperlogic pfx (regtangle), 1 = use own pfx (circle)
        usr_type = certificate_type_id

        # BUCKET_COMMON_FILE_NAME = bucket_name
        KEY_TEMPLATE_CIRCLE = local_imprint_folder / 'circle.pdf'
        KEY_TEMPLATE_RECT = local_imprint_folder / 'rectangle.pdf'
        LOCAL_TEMPLATE_PDF = KEY_TEMPLATE_RECT

        FONT_FILE_NAME = 'NotoSansJP-Medium.ttf'
        FONT_NAME = 'NotoSansJP'
        FONT_SIZE = 42

        if usr_type == 0:
            LOCAL_TEMPLATE_PDF = KEY_TEMPLATE_RECT

        if usr_type == 1:
            LOCAL_TEMPLATE_PDF = KEY_TEMPLATE_CIRCLE

        if usr_type == 2:
            LOCAL_TEMPLATE_PDF = KEY_TEMPLATE_RECT

        # case company seal...
        isCompanySeal = certificate_type_id == 2
        if isCompanySeal:
            LOCAL_TEMPLATE_PDF = KEY_TEMPLATE_RECT

        vis_file_name = str(usr_id) + '_'+str(usr_type)+'_vis_signature.pdf'

        LOCAL_FONT = local_imprint_folder / 'NotoSansJP-Medium.ttf'

        save_vis_tmp = local_tmp_folder / vis_file_name

        # name of the file to save
        usr_sign_pic_pdf = save_vis_tmp

        # fnt = ImageFont.load_default()
        image_w = 600
        image_h = 600

        # SET FONT OBJ FOR CALCULATE WRAP TEXT
        fnt = ImageFont.truetype(LOCAL_FONT, FONT_SIZE)
        # start to create text  then merge to template pdf by reportlab and pypdf2
        packet = io.BytesIO()

        # Create a new canvas with Reportlab
        can = canvas.Canvas(packet, pagesize=letter)

        # register font for using
        pdfmetrics.registerFont(TTFont(FONT_NAME, LOCAL_FONT))
        # SET FONT COLOR
        can.setFillColorRGB(1, 0, 0)
        # SET FONT AND SIZE
        can.setFont(FONT_NAME, FONT_SIZE)

        # calculate and wrap long string (company name)
        para = text_wrap(company, fnt, image_w-100)
        # if usr_type == 0 create rectangle
        if usr_type == 0:
            current_h, pad = image_h - 100, 10
        else:  # guest, create  circle
            current_h, pad = image_h - 180, 10

        # write company name
        for line in para:
            w = pdfmetrics.stringWidth(line, FONT_NAME, FONT_SIZE)
            h = FONT_SIZE

            can.drawString((image_w - w) / 2, current_h, line)
            current_h -= h + pad

        # calculate position for other data
        y_position_name = 0
        y_position_date = 0
        pad = 10
        if usr_type == 0:
            y_position_name = 180
            y_position_date = 100
        else:  # guest, create  circle
            y_position_name = 200
            y_position_date = 100
        # write name
        # calculate and wrap long string (username)
        name_para = text_wrap(name, fnt, image_w - 100, 3)
        index = 1
        # write username
        for line in name_para:
            w = pdfmetrics.stringWidth(line, FONT_NAME, FONT_SIZE)
            h = FONT_SIZE

            can.drawString(
                (image_w - w) / 2,
                y_position_name + (len(name_para) - index) * (h + pad),
                line
            )
            index += 1

        # write date
        w = pdfmetrics.stringWidth(today, FONT_NAME, FONT_SIZE)
        h = FONT_SIZE
        can.drawString((image_w - w) / 2, y_position_date, today)

        # save canvas
        can.showPage()
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # create pdf from buffer
        new_pdf = PdfReader(packet)

        # Read template PDF
        existing_pdf = PdfReader(open(LOCAL_TEMPLATE_PDF, "rb"))
        output = PdfWriter()

        # Merge created canvas to template pdf
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

        # Finally, write "output" to a real file to tmp
        outputStream = open(usr_sign_pic_pdf, "wb")
        output.write(outputStream)
        outputStream.close()

        response = {
            'check': True,
            'message': 'success',
            'vis_name': vis_file_name,
            'tmp_vist_file': usr_sign_pic_pdf
        }

    except Exception as e:
        response = {
            'check': False,
            'message': str(e),
            'error': 'create-imprint',
        }

    return response

def validate_position(sign_left, sign_bottom, sign_width_left, sign_height_bottom, page_width, page_height):
    if sign_left < 0 or sign_bottom < 0:
        return False
    if sign_left >= page_width or sign_bottom >= page_height:
        return False
    if sign_width_left > page_width or sign_height_bottom > page_height:
        return False
    return True


def prepare_document_imprint(local_imprint_folder, local_tmp_folder, input_file, PDF_PWD, user_info, pki, position):
    if not position:
        return False, None, None, None, ''
    
    visualize_optlist = {}

    try:
        sign_page = int(position.get('page', 0))
        
        sign_width = int(position.get('width', 60))
        sign_height = int(position.get('height', 60))

        sign_left = int(position.get('left', 0))
        sign_bottom = int(position.get('bottom', 0))
        sign_width_left = sign_width + sign_left if sign_width is not None and sign_left is not None else None
        sign_height_bottom = sign_height + sign_bottom if sign_height is not None and sign_bottom is not None else None

        width, height, total_pages = _get_page_dimensions(input_file, PDF_PWD, sign_page)

        if any(key not in position for key in ['left', 'bottom']):
            res_sign_pos = cal_sign_location(width)
            sign_left = sign_left or int(res_sign_pos['L'])
            sign_bottom = sign_bottom or int(res_sign_pos['B'])
            sign_width_left = sign_width_left or int(res_sign_pos['LW'])
            sign_height_bottom = sign_height_bottom or int(res_sign_pos['BH'])
        
        if not validate_position(sign_left, sign_bottom, sign_width_left, sign_height_bottom, width, height):
            return False, None, None, None, 'error.position.invalid'

        visualize_optlist = {
            'sign_page': sign_page,
            'sign_left': sign_left,
            'sign_bottom': sign_bottom,
            'sign_width_left': sign_width_left,
            'sign_height_bottom': sign_height_bottom
        }

        vis_page = 0
        resp_crt_sign_vist = create_vis_file(local_imprint_folder, local_tmp_folder, user_info, pki)

        if not resp_crt_sign_vist['check']:
            raise Exception(resp_crt_sign_vist['message'])

        local_visfile = resp_crt_sign_vist['tmp_vist_file']
            
        visualize_location = (visualize_optlist['sign_left'], visualize_optlist['sign_bottom'], visualize_optlist['sign_width_left'], visualize_optlist['sign_height_bottom'])
        vis_page = int(visualize_optlist['sign_page'])

        if vis_page < 0 or vis_page >= total_pages:
            vis_page = 0

        return True, visualize_location, vis_page, local_visfile, 'success'
    
    except Exception as e:
        print('Imprint Error:', e)
        return False, None, None, None, 'error.position.failure'
