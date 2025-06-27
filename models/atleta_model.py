# Modelo para gestión de atletas
import mysql.connector
from mysql.connector import Error
from .database import Database

class AtletaModel:
    def __init__(self):
        self.db = Database()
    
    def insert_atleta(self, id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            
            cursor.execute("SELECT duracion_dias FROM planes WHERE id_plan = %s", (id_plan,))
            plan_result = cursor.fetchone()
            
            if not plan_result:
                print(f"Error: Plan {id_plan} no existe")
                return None
                
            duracion_dias = plan_result[0]
            
            from datetime import datetime, timedelta
            fecha_inscripcion = datetime.now().date()
            fecha_vencimiento = fecha_inscripcion + timedelta(days=duracion_dias)
            
            cursor.execute("""
                INSERT INTO `atletas`
                (`id_usuario`, `cedula`, `peso`, `fecha_nacimiento`, `fecha_inscripcion`, `fecha_vencimiento`, `id_plan`, `id_coach`, `meta_largo_plazo`, `valoracion_especiales`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_usuario, cedula, peso, fecha_nacimiento, fecha_inscripcion, fecha_vencimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales))
            
            self.db.connection.commit()
            new_id = cursor.lastrowid
            print(f"Nuevo atleta insertado con ID: {new_id}, vence: {fecha_vencimiento}")
            return new_id

        except mysql.connector.Error as error:
            print(f"Error al ingresar datos {error}")
            # Devolver None en caso de error para una mejor validación en el controlador
            return None

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            self.db.disconnect()
    
    def read_atletas(self):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM `atletas` WHERE 1")
            result = cursor.fetchall()
            return result
        
        except mysql.connector.Error as error:
            print(f"Error al consultar datos {error}")
            return []

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            self.db.disconnect()

    def update_atleta(self, id_atleta, id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            
            cursor.execute("SELECT id_plan FROM atletas WHERE id_atleta = %s", (id_atleta,))
            plan_actual = cursor.fetchone()
            
            if plan_actual and plan_actual[0] != id_plan:
                cursor.execute("SELECT duracion_dias FROM planes WHERE id_plan = %s", (id_plan,))
                plan_result = cursor.fetchone()
                
                if plan_result:
                    from datetime import datetime, timedelta
                    fecha_vencimiento = datetime.now().date() + timedelta(days=plan_result[0])
                    
                    cursor.execute("""
                        UPDATE `atletas` SET 
                        `id_usuario`=%s, `cedula`=%s, `peso`=%s, `fecha_nacimiento`=%s, 
                        `id_plan`=%s, `id_coach`=%s, `meta_largo_plazo`=%s, `valoracion_especiales`=%s,
                        `fecha_vencimiento`=%s
                        WHERE `id_atleta`=%s
                    """, (id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales, fecha_vencimiento, id_atleta))
                else:
                    print(f"Error: Plan {id_plan} no existe")
                    return False
            else:
                cursor.execute("""
                    UPDATE `atletas` SET 
                    `id_usuario`=%s, `cedula`=%s, `peso`=%s, `fecha_nacimiento`=%s, 
                    `id_plan`=%s, `id_coach`=%s, `meta_largo_plazo`=%s, `valoracion_especiales`=%s
                    WHERE `id_atleta`=%s
                """, (id_usuario, cedula, peso, fecha_nacimiento, id_plan, id_coach, meta_largo_plazo, valoracion_especiales, id_atleta))
            
            self.db.connection.commit()
            print(f"Atleta {id_atleta} actualizado correctamente")
            return True

        except mysql.connector.Error as error:
            print(f"Error al actualizar datos {error}")
            return False

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            self.db.disconnect()


    def actualizar_estado_membresia(self, id_atleta, fecha_vencimiento, estado_solvencia):
        """Actualiza solo el estado de membresía del atleta"""
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            
            cursor.execute("""
                UPDATE atletas 
                SET fecha_vencimiento = %s, estado_solvencia = %s 
                WHERE id_atleta = %s
            """, (fecha_vencimiento, estado_solvencia, id_atleta))
            
            self.db.connection.commit()
            print(f"Estado de membresía actualizado para atleta {id_atleta}")
            return cursor.rowcount > 0
            
        except mysql.connector.Error as error:
            print(f"Error al actualizar estado de membresía: {error}")
            return False
            
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            self.db.disconnect()

    def delete_atleta(self, id_atleta):
        try:
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("DELETE FROM `atletas` WHERE `id_atleta`=%s", (id_atleta,))
            self.db.connection.commit()
            # Verificar si la eliminación fue exitosa
            return cursor.rowcount > 0

        except mysql.connector.Error as error:
            print(f"Error al eliminar datos {error}")
            return False
            
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            self.db.disconnect()