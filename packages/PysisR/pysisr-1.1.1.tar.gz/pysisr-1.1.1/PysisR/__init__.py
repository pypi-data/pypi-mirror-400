__version__ = "1.1.1"

print("PysisR paketi yüklendi!")

# Kullanıcının pip ile yüklediğinde otomatik çalışacak kodlar
# Senin verdiğin konsept kodları ekleyelim:

class Create:
    @staticmethod
    def goto_create():
        print("pip adı oluşturuldu: PysisR")
        return "PysisR"

class Doc:
    @staticmethod
    def goto_create():
        print("README.md oluşturuldu")
        return "README.md"

class CodePlugin:
    @staticmethod
    def goto_create():
        print("Eklenti eklendi")
        return "Plugin"

class Plugin:
    @staticmethod
    def goto_bar(name):
        print(f"Eklenti aktif: {name}")

class TempPlugin:
    @staticmethod
    def goto_create():
        print("Temp plugin oluşturuldu")
        return "TempPlugin"

# Örnek kullanım
pip_name = Create.goto_create()
aciklama = Doc.goto_create()
code = CodePlugin.goto_create()
Plugin.goto_bar("ÖrnekEklenti")
temp_plugin = TempPlugin.goto_create()
