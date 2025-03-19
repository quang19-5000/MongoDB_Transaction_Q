from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.client_session import ClientSession

# Thông tin kết nối MongoDB
MONGO_URI = "mongodb+srv://quang10a2k38:Qh3102dt@cluster0.rgbbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Kết nối MongoDB
client = MongoClient(MONGO_URI)
db = client["bank"]
accounts = db["accounts"]

def check_balance(user_id):
    """
    Kiểm tra số dư của một tài khoản trong MongoDB.
    """
    user = accounts.find_one({"_id": user_id})
    if user:
        print(f"Số dư của {user_id}: {user['balance']} VND")
    else:
        print(f"Không tìm thấy tài khoản {user_id}.")

def transfer_money(session: ClientSession, sender: str, receiver: str, amount: int):
    """
    Thực hiện giao tác tập trung: chuyển tiền từ sender sang receiver trong cùng một collection.
    """
    try:
        session.start_transaction()

        result1 = accounts.update_one(
            {"_id": sender, "balance": {"$gte": amount}}, 
            {"$inc": {"balance": -amount}},
            session=session
        )

        # Nếu không có đủ tiền, hủy transaction
        if result1.modified_count == 0:
            raise ValueError("Số dư không đủ để thực hiện giao dịch.")

        # Thêm tiền vào receiver
        result2 = accounts.update_one(
            {"_id": receiver},
            {"$inc": {"balance": amount}},
            session=session
        )

        # Nếu không thành công, rollback transaction
        if result2.modified_count == 0:
            raise ValueError("Không tìm thấy tài khoản người nhận.")

        # Commit giao dịch nếu tất cả đều thành công
        session.commit_transaction()
        print("Giao dịch thành công!")

    except Exception as e:
        session.abort_transaction()  # Rollback nếu có lỗi
        print(f"Giao dịch thất bại: {e}")

# Kiểm tra số dư trước khi giao dịch
check_balance("user_A")
check_balance("user_B")

# Bắt đầu session và thực hiện giao dịch
with client.start_session() as session:
    transfer_money(session, "user_B", "user_A", 300)  # Thay đổi số tiền để thử nghiệm

# Kiểm tra số dư sau khi giao dịch
check_balance("user_A")
check_balance("user_B")

# Đóng kết nối MongoDB
client.close()
