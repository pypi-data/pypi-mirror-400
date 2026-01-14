import os
import sys
import json
import subprocess
import ntpath
import pathlib, html

from AnyQt.QtWidgets import QApplication, QLabel, QPushButton
from AnyQt.QtCore import pyqtSignal
from Orange.widgets import widget
from AnyQt.QtGui import QTextCursor, QTextCharFormat, QFont, QColor, QDesktopServices
from AnyQt.QtCore import QUrl

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import get_local_store_path
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from Orange.widgets.orangecontrib.HLIT_dev.utils import hlit_python_api
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import convert
else:
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from orangecontrib.HLIT_dev.utils import hlit_python_api
    from orangecontrib.HLIT_dev.remote_server_smb import convert



id_RAG = "Request_RAG"
num_RAG = "input_0"

id_folder = "Folder"
num_folder = "input_0"

id_conv = "Conversations"
num_conv = "input_0"

id_generic = "Request_Generic"
num_generic = "input_0"

ip_port = "127.0.0.1:8000"


def data_to_json_str(workflow_id, num_input, col_names, col_types, values, timeout=100000000):
    payload = {
        "workflow_id": workflow_id,
        "timeout": timeout,
        "data": [
            {
                "num_input": num_input,
                "values": [
                    col_names,
                    col_types,
                    values
                ]
            }
        ]
    }
    return json.dumps(payload)


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWLeTigre(widget.OWWidget):
    name = "Le Tigre"
    description = "Pilotage du workflow de recherche documentaire et d'appel LLM"
    icon = "icons/tiger.png"
    category = "AAIT - ALGORITHM"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/tiger.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/ChatbotTigerODM_v2.ui")
    want_control_area = False
    priority = 1089

    signal_label_update = pyqtSignal(QLabel, str)

    def __init__(self):
        super().__init__()
        # Qt Management
        self.setFixedWidth(853)
        self.setFixedHeight(655)
        uic.loadUi(self.gui, self)

        # Chat area
        self.textBrowser_chat.setReadOnly(True)
        self.textBrowser_chat.setOpenLinks(False)  # Prevent internal navigation
        self.textBrowser_chat.anchorClicked.connect(self.handle_link_click)

        # Connect the buttons
        self.btn_send.clicked.connect(lambda: self.run(self.send_request))
        self.btn_folder.clicked.connect(lambda: self.run(self.load_folder))
        self.signal_label_update.connect(self.update_label)

        # Text styles
        self.fmt_normal = QTextCharFormat()  # Default plain text
        self.fmt_bold = QTextCharFormat()
        self.fmt_bold.setFontWeight(QFont.Weight.Bold)
        self.fmt_bold.setForeground(QColor("#2c3e50"))  # Optional: Dark blue-grey for names

        # Data
        self.thread = None
        self.model = None
        self.folder_is_selected = False
        self.store_path = get_local_store_path()

        # Fill conversations list
        self.update_conversations_list()


    def run(self, func):
        # Clear error & warning
        self.error("")
        self.warning("")

        # Disable all buttons
        for button in self.findChildren(QPushButton):
            button.setEnabled(False)
        self.list_conversations.setDisabled(True)

        # If Thread is already running, interrupt it
        if self.thread is not None:
            if self.thread.isRunning():
                self.thread.safe_quit()

        # Connect and start thread : main function, progress, result and finish
        self.thread = thread_management.Thread(func)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()


    def send_request(self, progress_callback=None):
        # Get the request, return if it's empty
        request = self.textEdit_request.toPlainText()
        if not request:
            return

        # If no folder was selected
        if not self.folder_is_selected:
            self.error("Select a folder first.")
            return

        # Prepare the input json
        workflow_id = id_RAG
        num_input = num_RAG
        data_json = data_to_json_str(workflow_id=workflow_id,
                                     num_input=num_input,
                                     col_names=["content", "format"],
                                     col_types=["str", "str"],
                                     values=[[request, ""]])

        # Get the current text in the textBrowser (chat window)
        text = self.textBrowser_chat.toPlainText()
        if text:
            progress_callback(("chat", "\n\n"))

        # Add the request to the textBrowser (HTML format)
        progress_callback(("header", "Vous : "))
        progress_callback(("chat", f"{request}\n\n"))

        # Prepare for assistant's answer
        progress_callback(("header", "Le Tigre : "))

        # POST Input
        hlit_python_api.post_input_to_workflow(ip_port=ip_port, data=data_json)

        # GET Status / Output
        while True:
            response = hlit_python_api.call_output_workflow_unique_2(ip_port=ip_port, workflow_id=workflow_id)
            if response:
                status = response["_statut"]
                # If EngineLLM has been reached
                if status == "Stream":
                    # Open the stream route and get the tokens
                    url = f"http://{ip_port}/chat/{workflow_id}"
                    stream_answer(url=url, progress_callback=progress_callback)
                # Or if there are defined status
                elif status is not None and status != "Finished":
                    # Display them in the UI (label)
                    self.signal_label_update.emit(self.label_freeText, status)
                # Or if Output Interface has been reached
                elif status == "Finished":
                    # Get the data in Output Interface (source table with "path", "name", "page") and exit the loop
                    data = convert.convert_json_implicite_to_data_table(response["_result"])
                    break
                # Else, do nothing while waiting for infos
                else:
                    pass

        # Check if data is defined
        if not data:
            self.error("Could not display sources, no table was retrieved from Output Interface.")
            return
        # Check if the sources data table contains the required columns
        required_columns = ["path", "name", "page"]
        if not all(col in data.domain for col in required_columns):
            self.error('Could not display sources, the following columns are needed in the result: "path", "name", "page".')
            return
        # Display sources from Output Interface, as HTML links
        progress_callback(("chat", "\n\n"))
        for row in data:
            path = pathlib.Path(row["path"].value)
            name = row["name"].value
            page = row["page"].value
            file_url = path.as_uri()
            progress_callback(("sources", f'<a href="{file_url}">{html.escape(name)}</a>&nbsp;- Page {int(page)}<br>'))


    def load_folder(self):
        # Prepare the input json
        workflow_id = id_folder
        num_input = num_folder
        data_json = data_to_json_str(workflow_id=workflow_id,
                                     num_input=num_input,
                                     col_names=["trigger"],
                                     col_types=["str"],
                                     values=[["Trigger"]])

        # POST Input
        hlit_python_api.post_input_to_workflow(ip_port=ip_port, data=data_json)

        # GET Status / Output
        while True:
            response = hlit_python_api.call_output_workflow_unique_2(ip_port=ip_port, workflow_id=workflow_id)
            if response:
                status = response["_statut"]
                # If Output Interface has been reached
                if status == "Finished":
                    # Get the data in Output Interface (folder table with "path") and exit the loop
                    data = convert.convert_json_implicite_to_data_table(response["_result"])
                    break
                # Or if there are defined status
                elif status is not None:
                    # Display them in the UI (label)
                    self.signal_label_update.emit(self.label_freeText, status)
                # Else, do nothing while waiting for infos
                else:
                    pass

        # Check if data is defined
        if not data:
            self.error("Cannot display the selected folder, no table was retrieved from Output Interface.")
            return
        # Check if the data table contains the required column
        required_columns = ["path"]
        if not all(col in data.domain for col in required_columns):
            self.error('Cannot display the selected folder, the following column is needed in the result: "path".')
            return
        # Display folder to its label
        path = data[0]["path"].value
        folder_name = ntpath.basename(path)
        self.signal_label_update.emit(self.label_folder, folder_name)
        self.signal_label_update.emit(self.label_freeText, "Préparation terminé !")
        self.folder_is_selected = True


    def load_conversation(self, progress_callback=None):
        # Clear textBrowser history
        progress_callback(("clear", 0))

        # Find the selected item
        item = self.list_conversations.currentItem()
        # Find its associated file
        path = os.path.join(self.store_path, "conversations", item.text() + ".pkl")
        # If the file doesn't exist, error
        if not os.path.exists(path):
            self.error(f"Conversation could not be loaded, the file {path} does not exist.")

        # Prepare the input json
        workflow_id = id_conv
        num_input = num_conv
        data_json = data_to_json_str(workflow_id=workflow_id,
                                     num_input=num_input,
                                     col_names=["path"],
                                     col_types=["str"],
                                     values=[[path]])

        # POST Input
        hlit_python_api.post_input_to_workflow(ip_port=ip_port, data=data_json)

        # GET Status / Output
        while True:
            response = hlit_python_api.call_output_workflow_unique_2(ip_port=ip_port, workflow_id=workflow_id)
            if response:
                status = response["_statut"]
                # If Output Interface has been reached
                if status == "Finished":
                    # Get the data in Output Interface (conversation table with "request", "Answer") and exit the loop
                    data = convert.convert_json_implicite_to_data_table(response["_result"])
                    break
        # Check if data is defined
        if not data:
            self.error("Cannot display the selected conversation, no table was retrieved from Output Interface.")
            return
        # Check if the data table contains the required column
        required_columns = ["request", "Answer"]
        if not all(col in data.domain for col in required_columns):
            self.error('Cannot display the selected conversation, the following columns are needed in the result: "request", "Answer.')
            return
        # Display the conversation
        self.display_conversation(data, progress_callback)


    def handle_progress(self, value) -> None:
        # Gestion du textBrowser selon différents Tags
        tag, content = value[0], value[1]
        cursor = self.textBrowser_chat.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if tag == "chat":
            cursor.insertText(content, self.fmt_normal)
        elif tag == "header":
            cursor.insertText(content, self.fmt_bold)
        elif tag == "sources":
            cursor.insertHtml(content)
            cursor.setCharFormat(self.fmt_normal)  # Immediate reset
        elif tag == "clear":
            self.textBrowser_chat.clear()
            return
        self.textBrowser_chat.setTextCursor(cursor)

    def handle_result(self, result):
        if result:
            self.label_folder.setText(result)

    def handle_finish(self):
        for button in self.findChildren(QPushButton):
            button.setEnabled(True)
        self.list_conversations.setDisabled(False)


    def post_initialized(self):
        pass


    def update_conversations_list(self):
        self.list_conversations.clear()
        convs_path = os.path.join(self.store_path, "conversations")
        if not os.path.exists(convs_path):
            return
        else:
            files = [f for f in os.listdir(convs_path) if os.path.isfile(os.path.join(convs_path, f))]
            for file in files:
                name, _ = os.path.splitext(file)
                self.list_conversations.addItem(name)
        self.list_conversations.itemClicked.connect(lambda: self.run(self.load_conversation))


    def display_conversation(self, data, progress_callback):
        # Iterate over rows
        for row in data:
            # "request" is the user input
            user = row["request"].value
            progress_callback(("header", "Vous : "))
            progress_callback(("chat", f"{user}\n\n"))
            # "Answer" is the assistant's answer
            assistant = row["Answer"].value
            progress_callback(("header", "Le Tigre : "))
            progress_callback(("chat", f"{assistant}\n\n"))


    def update_label(self, label, text):
        label.setText(text)

    def handle_link_click(self, url: QUrl):
        # QDesktopServices.openUrl uses the OS default handler
        QDesktopServices.openUrl(url)


# Chattyboy Streaming Shitshow
def stream_answer(url, progress_callback):
    full_text = ""
    cmd = ["curl", "-s", "-N", url]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0
    )
    try:
        while True:
            chunk = proc.stdout.read(1024)  # read raw bytes
            if not chunk:
                break
            token = chunk.decode("utf-8", errors="ignore")
            if "<|im_end|>" in token or "[DONE]" in token:
                break
            else:
                progress_callback(("chat", token))
            full_text += token
    finally:
        proc.stdout.close()
        proc.wait()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWLeTigre()
    my_widget.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
