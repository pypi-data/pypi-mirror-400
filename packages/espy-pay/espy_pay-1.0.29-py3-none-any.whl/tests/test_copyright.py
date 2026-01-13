import os

def test_copyright():
    cwd = os.getcwd()
    directory = f'{cwd}/espy_pay'
    failed_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == '__init__.py' or file.endswith('.json'):
                continue
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                content = f.read()
                if """Copyright 2024 Everlasting Systems and Solutions LLC (www.myeverlasting.net).
All Rights Reserved.

No part of this software or any of its contents may be reproduced, copied, modified or adapted, without the prior written consent of the author, unless otherwise indicated for stand-alone materials.

For permission requests, write to the publisher at the email address below:
office@myeverlasting.net

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

""" not in content:
                    failed_files.append(file_path)
    
    assert len(failed_files) == 0, f"The following files failed the copyright assert: {', '.join(failed_files)}"