from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Kết nối đến hai database MongoDB
MONGO_URI_DB1 = "mongodb+srv://quang10a2k38:Qh3102dt@cluster0.rgbbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_URI_DB2 = "mongodb+srv://quang10a2k38:Qh3102dt@cluster0.rgbbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Tạo client cho mỗi database
client_db1 = MongoClient(MONGO_URI_DB1)
client_db2 = MongoClient(MONGO_URI_DB2)

# Chọn database và collection tương ứng
db1 = client_db1["bank1"]
accounts_db1 = db1["accounts"]

db2 = client_db2["bank2"]
accounts_db2 = db2["accounts"]

# Hàm tạo người dùng ở hai cơ sở dữ liệu khác nhau
def setup_users():
    """Tạo người dùng trong hai database nếu chưa có."""
    try:
        if accounts_db1.count_documents({"_id": "user_A"}) == 0:
            accounts_db1.insert_one({"_id": "user_A", "balance": 1000})
            print("User_A đã được tạo trong database 1.")

        if accounts_db2.count_documents({"_id": "user_B"}) == 0:
            accounts_db2.insert_one({"_id": "user_B", "balance": 500})
            print("User_B đã được tạo trong database 2.")

    except PyMongoError as e:
        print(f"Lỗi khi tạo người dùng: {e}")

# Hàm thực hiện giao dịch giữa hai cơ sở dữ liệu
def transfer_money(sender, receiver, amount, sender_db, receiver_db):
    # Chọn đúng client và collection
    sender_client, sender_accounts = (client_db1, accounts_db1) if sender_db == "db1" else (client_db2, accounts_db2)
    receiver_client, receiver_accounts = (client_db1, accounts_db1) if receiver_db == "db1" else (client_db2, accounts_db2)

    session_sender = sender_client.start_session()
    session_receiver = receiver_client.start_session()

    try:
        with session_sender.start_transaction():
            with session_receiver.start_transaction():
                # Kiểm tra số dư của người gửi
                sender_account = sender_accounts.find_one({"_id": sender}, session=session_sender)
                if not sender_account or sender_account["balance"] < amount:
                    raise ValueError(f"Số dư của {sender} không đủ để thực hiện giao dịch!")

                # Kiểm tra người nhận
                receiver_account = receiver_accounts.find_one({"_id": receiver}, session=session_receiver)
                if not receiver_account:
                    raise ValueError(f"Tài khoản {receiver} không tồn tại!")

                # Trừ tiền từ người gửi
                result1 = sender_accounts.update_one(
                    {"_id": sender},
                    {"$inc": {"balance": -amount}},
                    session=session_sender
                )

                # Thêm tiền vào người nhận
                result2 = receiver_accounts.update_one(
                    {"_id": receiver},
                    {"$inc": {"balance": amount}},
                    session=session_receiver
                )

                # Kiểm tra nếu cả hai cập nhật thành công
                if result1.modified_count > 0 and result2.modified_count > 0:
                    session_sender.commit_transaction()
                    session_receiver.commit_transaction()
                    print(f"Giao dịch thành công: Chuyển {amount} từ {sender} ➝ {receiver}")
                else:
                    raise RuntimeError("Không thể cập nhật số dư cho một trong hai tài khoản!")

    except (PyMongoError, ValueError, RuntimeError) as e:
        # Hoàn tác giao dịch nếu xảy ra lỗi
        try:
            session_sender.abort_transaction()
        except PyMongoError:
            print("Giao dịch trong database người gửi đã được hủy bỏ trước đó!")

        try:
            session_receiver.abort_transaction()
        except PyMongoError:
            print("Giao dịch trong database người nhận đã được hủy bỏ trước đó!")

        print(f"Giao dịch thất bại, hoàn tác thay đổi. Lỗi: {e}")

    finally:
        session_sender.end_session()
        session_receiver.end_session()

# Chạy chương trình
if __name__ == "__main__":
    # Tạo hai người dùng ở hai cơ sở dữ liệu
    setup_users()

    # Giao dịch: Chuyển 300 từ user_A (trong db1) sang user_B (trong db2)
    transfer_money("user_A", "user_B", 300, sender_db="db1", receiver_db="db2")

    # Giao dịch: Chuyển 1500 từ user_B (trong db2) sang user_A (trong db1)
    # transfer_money("user_B", "user_A", 1500, sender_db="db2", receiver_db="db1")

    # Kiểm tra số dư sau giao dịch
    print("\nDữ liệu trong database 1:")
    for account in accounts_db1.find():
        print(account)

    print("\nDữ liệu trong database 2:")
    for account in accounts_db2.find():
        print(account)

    # Đóng kết nối
    client_db1.close()
    client_db2.close()
