import cups
from flask import Flask, jsonify, request
from flask_swagger import swagger

app = Flask(__name__)

# เชื่อมต่อกับ CUPS
conn = cups.Connection()


@app.route('/print', methods=['POST'])
def print_file():
    """
    Print
    ---
    tags:
      - users
    definitions:
      - schema:
          id: Group
          properties:
            name:
             type: string
             description: the group's name
    parameters:
      - in: body
        name: body
        schema:
          id: User
          required:
            - email
            - name
          properties:
            email:
              type: string
              description: email for user
            name:
              type: string
              description: name for user
            address:
              description: address for user
              schema:
                id: Address
                properties:
                  street:
                    type: string
                  state:
                    type: string
                  country:
                    type: string
                  postalcode:
                    type: string
            groups:
              type: array
              description: list of groups
              items:
                $ref: "#/definitions/Group"
    responses:
      201:
        description: User created
    """
    try:
        # รับข้อมูลจาก request เช่น URL ของไฟล์ที่ต้องการพิมพ์ หรือเส้นทางของไฟล์ในระบบ
        file_path = request.json.get('file_path')
        printer_name = request.json.get('printer_name')

        if not file_path or not printer_name:
            return jsonify({"error": "file_path or printer_name is missing"}), 400

        # ตรวจสอบว่าเครื่องพิมพ์มีอยู่จริง
        printers = conn.getPrinters()
        if printer_name not in printers:
            return jsonify({"error": "Printer not found"}), 404

        # ส่งงานพิมพ์ไปที่เครื่องพิมพ์
        print_job_id = conn.printFile(printer_name, file_path, "Print Job", {})

        return jsonify({"message": "Print job submitted", "job_id": print_job_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/printers', methods=['GET'])
def get_printers():
    try:
        # ดึงรายชื่อเครื่องพิมพ์ทั้งหมดที่เชื่อมต่ออยู่
        printers = conn.getPrinters()

        # สร้าง list ของเครื่องพิมพ์เพื่อตอบสนอง
        printer_list = []
        for printer_name, printer_info in printers.items():
            printer_list.append({
                "name": printer_name,
                "description": printer_info["printer-info"],
                "status": printer_info["printer-state-message"],
                "is_default": printer_info.get("printer-is-default", False)
            })

        return jsonify({"printers": printer_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Printer APIs"
    return jsonify(swag)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
