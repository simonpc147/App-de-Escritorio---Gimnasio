from models.rutina_model import RutinaModel

class RutinaController:
    def __init__(self):
        self.model = RutinaModel()
    
    def crear_rutina(self, nombre_rutina, nivel, descripcion, creado_por):
        return self.model.insert_rutina(nombre_rutina, nivel, descripcion, creado_por)
    
    def obtener_rutinas(self):
        return self.model.read_rutinas()
    
    def actualizar_rutina(self, id_rutina, nombre_rutina, nivel, descripcion):
        return self.model.update_rutina(id_rutina, nombre_rutina, nivel, descripcion)
    
    def eliminar_rutina(self, id_rutina):
        return self.model.delete_rutina(id_rutina)
    
    def crear_ejercicio(self, nombre_ejercicio, tipo_ejercicio, descripcion, instrucciones):
        return self.model.insert_ejercicio(nombre_ejercicio, tipo_ejercicio, descripcion, instrucciones)
    
    def obtener_ejercicios(self):
        return self.model.read_ejercicios()
    
    def asignar_ejercicio_a_rutina(self, id_rutina, id_ejercicio, nivel, series, rondas, orden_ejercicio):
        return self.model.asignar_ejercicio_rutina(id_rutina, id_ejercicio, nivel, series, rondas, orden_ejercicio)
    
    def obtener_rutina_completa(self, id_rutina):
        return self.model.get_rutina_completa(id_rutina)

    def contar_ejercicios_rutina(self, id_rutina):
        return self.model.contar_ejercicios_rutina(id_rutina)
    
    def eliminar_ejercicio_de_rutina(self, id_rutina, id_ejercicio):
        return self.model.eliminar_ejercicio_de_rutina(id_rutina, id_ejercicio)