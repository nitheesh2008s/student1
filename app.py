import streamlit as st
from PIL import Image
from io import BytesIO
import json 
import numpy as np
import os
import hashlib
import time
import cv2
from pyzbar.pyzbar import decode





if "wrong_attempts" not in st.session_state:
    st.session_state.wrong_attempts = 0

# -------- USER FILE SETUP --------
USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------------- BLACK BACKGROUND ----------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #000000, #050a1f, #000000);
    color: #00ffea;
    font-family: Consolas, monospace;
}

/* TITLE GLOW */
h1, h2, h3 {
    color: #00fff2;
    text-shadow: 0 0 10px #00fff2, 0 0 20px #00fff2;
}

/* BUTTON STYLE */
.stButton > button {
    background-color: black;
    color: #00fff2;
    border: 1px solid #00fff2;
    box-shadow: 0 0 10px #00fff2;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #020617;
    border-right: 1px solid #00fff2;
}

/* INPUT BOX */
input, textarea {
    background-color: black !important;
    color: #00fff2 !important;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    border: 1px solid #00fff2;
    box-shadow: 0 0 10px #00fff2;
}

</style>
""", unsafe_allow_html=True)



# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        users = load_users()

        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")
            # ---------------- SIGNUP PAGE ----------------
def signup_page():
    st.title("📝 Register New Account")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Register"):

        users = load_users()

        if new_user in users:
            st.error("Username already exists")

        elif new_pass != confirm_pass:
            st.error("Passwords do not match")

        elif new_user == "" or new_pass == "":
            st.warning("Please fill all fields")

        else:
            users[new_user] = new_pass
            save_users(users)
            st.success("Account created successfully! Go to Login.")
    


# ---------------- LOGOUT ----------------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()


# ---------------- ENCODE FUNCTION ----------------
def encode_image(image, message):

    message += "###"   # end marker
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    img = image.convert("RGB")
    pixels = list(img.getdata())

    if len(binary_message) > len(pixels) * 3:
        raise ValueError("Message too large for this image")

    new_pixels = []
    data_index = 0

    for pixel in pixels:
        r, g, b = pixel

        if data_index < len(binary_message):
            r = (r & ~1) | int(binary_message[data_index])
            data_index += 1

        if data_index < len(binary_message):
            g = (g & ~1) | int(binary_message[data_index])
            data_index += 1

        if data_index < len(binary_message):
            b = (b & ~1) | int(binary_message[data_index])
            data_index += 1

        new_pixels.append((r, g, b))

    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(new_pixels)

    return encoded_img


# ---------------- DECODE FUNCTION ----------------
def decode_image(image):
    binary_data = ""
    img = image.convert("RGB")
    pixels = list(img.getdata())

    for pixel in pixels:
        for value in pixel[:3]:
            binary_data += str(value & 1)

    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]

    decoded_message = ""
    for byte in all_bytes:
        if len(byte) < 8:
            break

        decoded_char = chr(int(byte, 2))
        decoded_message += decoded_char

        if decoded_message.endswith("###"):
            return decoded_message[:-3]

    return ""
#-----------ATTACK DETECTION---#

def detect_stego_attack(image):

    img_array = np.array(image)

    # Check noise level
    noise_level = np.std(img_array)

    # Basic threshold detection
    if noise_level > 80:
        return "⚠ High noise detected - possible steganography attack"

    # Check image format change
    if image.format != "PNG":
        return "⚠ Image format may have been recompressed"

    return "✅ Image appears normal"


# ---------------- MAIN APP ----------------
def main_app():

    # Sidebar
    st.sidebar.title("Navigation")
    st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")
    st.sidebar.write("Logged in as:", st.session_state.username)

    st.sidebar.markdown("🟢 Secure Session Active")
    st.sidebar.markdown("🔎 Monitoring Data Integrity")

    if st.sidebar.button("Logout"):
        logout()

    choice = st.sidebar.radio(
        "Select Operation",
        ["Encode Message", "Decode Message","Link Scanner","File Integrity Check","QR Scanner"]
    )

    st.title("🛡 CYBERSECURE STEGANOGRAPHY SYSTEM")

    st.markdown("### 🔐 Protecting Data Beyond Visibility")
    st.info("💻 Security is not a product, it's a process.")
    st.warning("⚠ Unauthorized access is strictly monitored.")
    st.success("🧬 Encrypt. Hide. Protect. Defend.")

    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        # -------- ENCODE --------
        if choice == "Encode Message":

            st.subheader("Hide Secret Message")
            message = st.text_area("Enter confidential message")
            expiry_minutes=st.number_input("Set message expiry time(minutes)",min_value=1,value=5)

            if st.button("Encode Message"):

                if message.strip() == "":
                    st.warning("Please enter a message")

                else:
                    expiry_time=int(time.time())+(expiry_minutes*60)
                    secret_message=f"{message}|EXP:{expiry_time}"
                    encoded_img = encode_image(image,secret_message)
                    st.session_state.encoded_img = encoded_img
                    st.session_state.show_download = True
                    st.success("Message hidden successfully")

            if st.session_state.get("show_download"):
                buffer = BytesIO()
                st.session_state.encoded_img.save(buffer, format="PNG")
                buffer.seek(0)

                st.download_button(
                    "Download Encoded Image",
                    buffer,
                    "encoded_image.png",
                    "image/png"
                )

        # -------- DECODE --------
        elif choice == "Decode Message":

          st.subheader("Extract Hidden Message")

    if st.button("Decode Message"):

        hidden_message = decode_image(image)

        if hidden_message:

            if "|EXP:" in hidden_message:

                parts = hidden_message.split("|EXP:")

                message_text = parts[0]
                expiry_time = int(parts[1])

                current_time = int(time.time())

                if current_time > expiry_time:
                    st.error("⚠ Message expired")
                else:
                    st.success("Hidden Message Retrieved")
                    st.text_area("Decoded Message", message_text)

            else:
                st.success("Hidden Message Retrieved")
                st.text_area("Decoded Message", hidden_message)

        else:
            st.error("No hidden message found")


         #-------------LINK DETECTOR-------
    elif choice == "Link Scanner":

         st.subheader("🛡 Human Firewall - Fake Link Detection")

    url = st.text_input("Enter URL to scan")

    if st.button("Scan Link"):

        if url == "":
            st.warning("Please enter a link")

        elif not url.startswith("https"):
            st.error("⚠ Unsafe Link ")

        elif any(word in url.lower() for word in ["login", "verify", "bank", "secure", "account"]):
            st.warning("⚠ Suspicious phishing link detected")

        elif any(char.isdigit() for char in url):
            st.warning("⚠ Link may contain suspicious characters")

        else:
            st.success("✅ Link looks safe")
    #-----FILE INTEGRITY CHECK-----
    elif choice == "File Integrity Check":

      st.subheader("🛡 File Integrity Verification")

    uploaded_file = st.file_uploader("Upload file to generate hash")

    if uploaded_file is not None:

        file_bytes = uploaded_file.read()

        hash_value = hashlib.sha256(file_bytes).hexdigest()

        st.success("File Hash Generated")

        st.text_area("SHA-256 Hash", hash_value, height=100)
        # -------- QR CODE PHISHING DETECTOR --------

    elif choice == "Scanner":

      st.subheader("🛡 QR Code Phishing Detector")

    uploaded_qr = st.file_uploader("Upload QR Code Image")

    if uploaded_qr is not None:

        file_bytes = np.asarray(bytearray(uploaded_qr.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        qr_codes = decode(img)

        if qr_codes:

            qr_data = qr_codes[0].data.decode("utf-8")

            st.write("QR Code Link:", qr_data)

            if "http://" in qr_data:
                st.error("⚠ Suspicious QR link detected")

            else:
                st.success("✅ QR link looks safe")

        else:
            st.warning("No QR code detected")

# ---------------- APP ROUTER ----------------
if "page" not in st.session_state:
    st.session_state.page = "login"


if st.session_state.logged_in:
    main_app()

else:
    if st.session_state.page == "login":
        login_page()
        if st.button("Create new account"):
            st.session_state.page = "signup"
            st.rerun()

    elif st.session_state.page == "signup":
        signup_page()
        if st.button("Back to Login"):
            st.session_state.page = "login"
            st.rerun()
            st.markdown("---")
st.markdown("🛡 Developed for Secure Digital Communication")
st.markdown("⚡ Cybersecurity • Encryption • Data Protection")