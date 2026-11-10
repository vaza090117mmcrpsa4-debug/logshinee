import os
import hmac
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from flask_mysqldb import MySQL


# ==================================================
# 1. CONFIGURACIÓN DEL SISTEMA
# ==================================================

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get(
        "FLASK_SECRET_KEY",
        "cambia_esta_clave_secreta"
    ),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MYSQL_HOST="localhost",
    MYSQL_USER="usr",
    MYSQL_PASSWORD="usr",
    MYSQL_DB="tiendita",
    MYSQL_CURSORCLASS="DictCursor"
)

mysql = MySQL(app)

USUARIO = os.environ.get("TIENDITA_USER", "admin")
CLAVE = os.environ.get("TIENDITA_PASSWORD", "password")


# ==================================================
# 2. FUNCIONES DE VALIDACIÓN
# ==================================================

def texto_obligatorio(valor, campo, limite=255):
    valor = (valor or "").strip()

    if not valor:
        raise ValueError(f"El campo {campo} es obligatorio.")

    if len(valor) > limite:
        raise ValueError(f"El campo {campo} es demasiado largo.")

    return valor


def validar_precio(valor, campo="precio"):
    try:
        precio = Decimal(str(valor).strip())
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"El {campo} debe ser numérico.")

    if not precio.is_finite() or precio < 0:
        raise ValueError(f"El {campo} no puede ser negativo.")

    if precio > Decimal("99999999.99"):
        raise ValueError(f"El {campo} supera el límite permitido.")

    return precio


def validar_entero(valor, campo, minimo=0):
    try:
        numero = int(str(valor).strip())
    except (ValueError, TypeError):
        raise ValueError(f"El campo {campo} debe ser un entero.")

    if str(numero) != str(valor).strip() or numero < minimo:
        raise ValueError(
            f"El campo {campo} debe ser un entero mayor o igual a {minimo}."
        )

    if numero > 2147483647:
        raise ValueError(f"El campo {campo} es demasiado grande.")

    return numero


def preparar_registros(registros):
    """Convierte valores de MySQL para mostrarlos en las plantillas."""
    es_uno = isinstance(registros, dict)
    lista = [registros] if es_uno else registros

    if not isinstance(lista, list):
        return registros

    for fila in lista:
        if not isinstance(fila, dict):
            continue

        for campo in ("unitario", "monto", "total", "precio_unitario"):
            if campo in fila and fila[campo] is not None:
                fila[campo] = float(fila[campo])

        for campo in ("stock", "cantidad"):
            if campo in fila and fila[campo] is not None:
                fila[campo] = int(fila[campo])

    return lista[0] if es_uno and lista else (None if es_uno else lista)


# ==================================================
# 3. PROTECCIÓN DE ACCESO
# ==================================================

def login_required(funcion):
    @wraps(funcion)
    def verificar(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Inicia sesión para continuar.", "error")
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return verificar


@app.after_request
def cabeceras_seguridad(respuesta):
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "SAMEORIGIN"
    respuesta.headers["Cache-Control"] = "no-store"
    return respuesta


# ==================================================
# 4. CONSULTAS A LA BASE DE DATOS
# ==================================================

def obtener_compras():
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            SELECT id_compra, nombre, marca, modelo,
                   presentacion, proveedor, unitario, stock
            FROM compras
            ORDER BY id_compra DESC
        """)
        return preparar_registros(cursor.fetchall())
    finally:
        cursor.close()


def obtener_ventas():
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            SELECT id_venta, cliente_dni, producto_ref,
                   cantidad, monto, fecha
            FROM ventas
            ORDER BY id_venta DESC
        """)
        return preparar_registros(cursor.fetchall())
    finally:
        cursor.close()


def obtener_compra(compra_id):
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            SELECT id_compra, nombre, marca, modelo,
                   presentacion, proveedor, unitario, stock
            FROM compras
            WHERE id_compra = %s
        """, (compra_id,))

        resultado = cursor.fetchone()
        return preparar_registros(resultado) if resultado else None
    finally:
        cursor.close()


def mostrar_inicio(compras=None, ventas=None,
                   search_query=None, compra_a_editar=None,
                   error_msg=None):
    try:
        if compras is None:
            compras = obtener_compras()

        if ventas is None:
            ventas = obtener_ventas()

        return render_template(
            "index.html",
            compras=compras,
            ventas=ventas,
            search_query=search_query,
            compra_a_editar=compra_a_editar,
            error_msg=error_msg
        )
    except Exception:
        app.logger.exception("Error al cargar el inventario.")
        return render_template(
            "index.html",
            compras=compras or [],
            ventas=ventas or [],
            search_query=search_query,
            compra_a_editar=compra_a_editar,
            error_msg="No se pudieron cargar los datos."
        )


# ==================================================
# 5. VERIFICAR ESTRUCTURA DE LA BASE DE DATOS
# ==================================================

def verificar_base_datos():
    cursor = mysql.connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INT AUTO_INCREMENT PRIMARY KEY,
                cliente_dni VARCHAR(255) NOT NULL,
                producto_ref VARCHAR(255) NOT NULL,
                cantidad INT NOT NULL DEFAULT 1,
                monto DECIMAL(10,2) NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("SHOW COLUMNS FROM compras LIKE 'stock'")

        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE compras
                ADD COLUMN stock INT NOT NULL DEFAULT 0
            """)

        cursor.execute("SHOW COLUMNS FROM ventas")
        columnas = {fila["Field"] for fila in cursor.fetchall()}

        definiciones = {
            "cliente_dni": "VARCHAR(255) NOT NULL DEFAULT ''",
            "producto_ref": "VARCHAR(255) NOT NULL DEFAULT ''",
            "cantidad": "INT NOT NULL DEFAULT 1",
            "monto": "DECIMAL(10,2) NOT NULL DEFAULT 0",
            "fecha": "TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP"
        }

        for columna, definicion in definiciones.items():
            if columna not in columnas:
                cursor.execute(
                    f"ALTER TABLE ventas ADD COLUMN {columna} {definicion}"
                )

        mysql.connection.commit()

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Error al verificar las tablas.")
        raise
    finally:
        cursor.close()


# ==================================================
# 6. INICIO DE SESIÓN
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("username", "").strip()
        clave = request.form.get("password", "")

        usuario_ok = hmac.compare_digest(usuario, USUARIO)
        clave_ok = hmac.compare_digest(clave, CLAVE)

        if usuario_ok and clave_ok:
            session.clear()
            session["logged_in"] = True
            session["username"] = usuario
            session.permanent = True

            flash("¡Bienvenido a Logshinee!", "success")
            return redirect(url_for("index"))

        flash("Usuario o contraseña incorrectos.", "error")

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("login"))


# ==================================================
# 7. INICIO DEL INVENTARIO
# ==================================================

@app.route("/")
@login_required
def index():
    try:
        verificar_base_datos()
        return mostrar_inicio()
    except Exception:
        return mostrar_inicio(
            compras=[],
            ventas=[],
            error_msg="Verifica que MySQL esté encendido y configurado."
        )


# ==================================================
# 8. AGREGAR PRODUCTOS
# ==================================================

@app.route("/add", methods=["POST"])
@login_required
def add():
    cursor = None

    try:
        datos = (
            texto_obligatorio(request.form.get("id_compra"), "ID"),
            texto_obligatorio(request.form.get("nombre"), "nombre"),
            texto_obligatorio(request.form.get("marca"), "marca"),
            texto_obligatorio(request.form.get("modelo"), "modelo"),
            texto_obligatorio(request.form.get("presentacion"), "presentación"),
            texto_obligatorio(request.form.get("proveedor"), "proveedor"),
            validar_precio(request.form.get("unitario"), "costo unitario"),
            validar_entero(request.form.get("stock", "0"), "stock")
        )

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO compras (
                id_compra, nombre, marca, modelo,
                presentacion, proveedor, unitario, stock
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, datos)

        mysql.connection.commit()
        flash("Producto agregado correctamente.", "success")

    except ValueError as error:
        mysql.connection.rollback()
        flash(str(error), "error")

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Error al agregar producto.")
        flash("No se pudo agregar. Verifica el ID y los datos.", "error")

    finally:
        if cursor:
            cursor.close()

    return redirect(url_for("index"))


# ==================================================
# 9. EDITAR PRODUCTOS
# ==================================================

@app.route("/edit/<int:compra_id>")
@login_required
def edit(compra_id):
    try:
        compra = obtener_compra(compra_id)

        if not compra:
            flash("Producto no encontrado.", "error")
            return redirect(url_for("index"))

        return mostrar_inicio(compra_a_editar=compra)

    except Exception:
        app.logger.exception("Error al abrir la edición.")
        flash("No se pudo abrir el producto.", "error")
        return redirect(url_for("index"))


@app.route("/update/<int:compra_id>", methods=["POST"])
@login_required
def update(compra_id):
    cursor = None

    try:
        datos = (
            texto_obligatorio(request.form.get("id_compra"), "ID"),
            texto_obligatorio(request.form.get("nombre"), "nombre"),
            texto_obligatorio(request.form.get("marca"), "marca"),
            texto_obligatorio(request.form.get("modelo"), "modelo"),
            texto_obligatorio(request.form.get("presentacion"), "presentación"),
            texto_obligatorio(request.form.get("proveedor"), "proveedor"),
            validar_precio(request.form.get("unitario"), "costo unitario"),
            validar_entero(request.form.get("stock", "0"), "stock"),
            compra_id
        )

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE compras
            SET id_compra = %s, nombre = %s, marca = %s,
                modelo = %s, presentacion = %s,
                proveedor = %s, unitario = %s, stock = %s
            WHERE id_compra = %s
        """, datos)

        cursor.execute(
            "SELECT id_compra FROM compras WHERE id_compra = %s",
            (datos[0],)
        )

        if not cursor.fetchone():
            raise ValueError("No se encontró el producto actualizado.")

        mysql.connection.commit()
        flash("Producto actualizado correctamente.", "success")

    except ValueError as error:
        mysql.connection.rollback()
        flash(str(error), "error")

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Error al actualizar producto.")
        flash("No se pudo actualizar. Verifica que el ID no se repita.", "error")

    finally:
        if cursor:
            cursor.close()

    return redirect(url_for("index"))


# ==================================================
# 10. ELIMINAR PRODUCTOS
# ==================================================

@app.route("/delete/<int:compra_id>", methods=["POST"])
@login_required
def delete(compra_id):
    cursor = None

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "DELETE FROM compras WHERE id_compra = %s",
            (compra_id,)
        )

        if cursor.rowcount == 0:
            flash("No se encontró el producto.", "warning")
        else:
            mysql.connection.commit()
            flash("Producto eliminado correctamente.", "success")

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Error al eliminar producto.")
        flash("No se pudo eliminar el producto.", "error")

    finally:
        if cursor:
            cursor.close()

    return redirect(url_for("index"))


# ==================================================
# 11. BUSCAR PRODUCTOS
# ==================================================

@app.route("/search", methods=["GET"])
@login_required
def search():
    busqueda = request.args.get("id_compra", "").strip()

    if not busqueda:
        flash("Escribe un ID para buscar.", "warning")
        return redirect(url_for("index"))

    cursor = None

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id_compra, nombre, marca, modelo,
                   presentacion, proveedor, unitario, stock
            FROM compras
            WHERE id_compra = %s
        """, (busqueda,))

        resultados = preparar_registros(cursor.fetchall())

        if resultados:
            flash("Producto encontrado.", "success")
        else:
            flash("No se encontraron resultados.", "warning")

        return mostrar_inicio(
            compras=resultados,
            ventas=obtener_ventas(),
            search_query=busqueda
        )

    except Exception:
        app.logger.exception("Error al buscar productos.")
        flash("Ocurrió un error durante la búsqueda.", "error")
        return redirect(url_for("index"))

    finally:
        if cursor:
            cursor.close()


# ==================================================
# 12. REGISTRAR VENTAS Y CONTROLAR STOCK
# ==================================================

@app.route("/add_sale", methods=["POST"])
@login_required
def add_sale():
    cursor = None

    try:
        cliente = texto_obligatorio(
            request.form.get("cliente_dni"), "cliente"
        )
        referencia = texto_obligatorio(
            request.form.get("producto_ref"), "producto"
        )
        cantidad = validar_entero(
            request.form.get("cantidad", "1"), "cantidad", 1
        )
        monto = validar_precio(
            request.form.get("monto"), "monto"
        )

        if monto == 0:
            raise ValueError("El monto de la venta debe ser mayor que cero.")

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT id_compra, nombre, stock
            FROM compras
            WHERE CAST(id_compra AS CHAR) = %s OR nombre = %s
            ORDER BY (CAST(id_compra AS CHAR) = %s) DESC
            LIMIT 1
            FOR UPDATE
        """, (referencia, referencia, referencia))

        producto = cursor.fetchone()

        if not producto:
            raise ValueError("El producto no existe en el inventario.")

        stock_actual = int(producto["stock"] or 0)

        if cantidad > stock_actual:
            raise ValueError(
                f"Stock insuficiente. Disponible: {stock_actual}; "
                f"solicitado: {cantidad}."
            )

        nuevo_stock = stock_actual - cantidad

        cursor.execute("""
            UPDATE compras
            SET stock = %s
            WHERE id_compra = %s
        """, (nuevo_stock, producto["id_compra"]))

        cursor.execute("""
            INSERT INTO ventas (
                cliente_dni, producto_ref, cantidad, monto
            )
            VALUES (%s, %s, %s, %s)
        """, (cliente, referencia, cantidad, monto))

        mysql.connection.commit()

        flash(
            f"Venta registrada. Stock restante: {nuevo_stock}.",
            "success"
        )

    except ValueError as error:
        mysql.connection.rollback()
        flash(str(error), "error")

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Error al registrar venta.")
        flash("No se pudo registrar la venta.", "error")

    finally:
        if cursor:
            cursor.close()

    return redirect(url_for("index"))


# ==================================================
# 13. EJECUTAR APLICACIÓN
# ==================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG", "1") == "1"
    )