import io
from bottle import route, run, request

@route('/upload', method='POST')
def do_upload():
    uploadfrom = request.forms.get('uploadfrom')
    if uploadfrom != 'take_picture':
        return 'failure'

    upload = request.files.get('picture')
    if not upload.filename.lower().endswith(('.jpg', '.jpeg')):
        return 'failure'

    filepath = 'files/' + upload.filename

    upload.save(filepath)

    return 'success'

run(host='0.0.0.0', port=8080, debug=True, reloader=False)
