class SceneLogic(object):
    def on_clear_action(self):
        # some special logic
        self.sceneServer.execute('clear')