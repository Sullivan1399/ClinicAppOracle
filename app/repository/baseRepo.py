from oracledb import AsyncConnection, DatabaseError
from fastapi import HTTPException

from app.utils.helper import await_if_needed

class BaseRepo:
    def __init__(self, db_conn: AsyncConnection = None):
        self.conn = db_conn

    # Function to catch and handle oracle Exceptions
    async def handle_execution(self, query: str, params: dict = None, commit: bool = False):
        if not self.conn:
             raise HTTPException(status_code=500, detail="Database connection lost")
        
        cursor = self.conn.cursor()
        try:
            if params:
                await cursor.execute(query, params)
            else:
                await cursor.execute(query)
            
            if commit:
                await self.conn.commit()
                return True
            
            # Nếu là câu lệnh SELECT, fetch dữ liệu
            if query.strip().upper().startswith("SELECT"):
                # Lưu ý: fetchall trả về list tuple, cần map sang dict ở tầng trên
                return await cursor.fetchall()
                
            return cursor # Trả về cursor cho các lệnh insert/update nếu cần lấy id
            
        except DatabaseError as e:
            error_obj, = e.args
            error_code = error_obj.code
            error_message = error_obj.message
            
            print(f"ORA Error: {error_code} - {error_message}")
            
            # Xử lý các lỗi phổ biến của Oracle Security
            if error_code == 28115: # ORA-28115: policy with check option violation (Lỗi VPD)
                raise HTTPException(status_code=403, detail="Truy cập bị từ chối: Vi phạm chính sách bảo mật dữ liệu (VPD).")
            if error_code == 942: # Table not found
                raise HTTPException(status_code=403, detail="Bạn không có quyền xem dữ liệu bảng này.")
            if error_code == 12406: # ORA-12406: policy violation (Lỗi OLS)
                raise HTTPException(status_code=403, detail="Truy cập bị từ chối: Cấp độ bảo mật không đủ (OLS).")
                
            raise HTTPException(status_code=400, detail=f"Database Error: {error_message}")
        finally:
            await await_if_needed(cursor.close())