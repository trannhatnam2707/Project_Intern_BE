import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone


def main():
    load_dotenv()

    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
    pinecone_namespace = os.getenv("PINECONE_NAMESPACE", "").strip()

    if not pinecone_api_key or not pinecone_index_name:
        print("❌ Thiếu PINECONE_API_KEY hoặc PINECONE_INDEX_NAME trong .env")
        sys.exit(1)

    force_yes = "--yes" in sys.argv

    namespace_label = pinecone_namespace if pinecone_namespace else "(default namespace)"
    print(f"🎯 Index: {pinecone_index_name}")
    print(f"🧩 Namespace: {namespace_label}")

    if not force_yes:
        confirm = input("⚠️ Bạn chắc chắn muốn xóa TOÀN BỘ vectors? Gõ YES để xác nhận: ")
        if confirm.strip() != "YES":
            print("⛔ Đã hủy thao tác.")
            return

    try:
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)

        before_stats = index.describe_index_stats()
        print(f"📊 Trước khi xóa: {before_stats}")

        if pinecone_namespace:
            index.delete(delete_all=True, namespace=pinecone_namespace)
        else:
            index.delete(delete_all=True)

        after_stats = index.describe_index_stats()
        print("✅ Đã xóa toàn bộ vectors thành công.")
        print(f"📊 Sau khi xóa: {after_stats}")
    except Exception as exc:
        print(f"❌ Xóa vectors thất bại: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
