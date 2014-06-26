def run():
    import nose

    from gcconfig import Config
    Config.init('unittest', False)

    import sys
    from os import path as osp
    setupcfg = osp.join(osp.abspath(osp.dirname(__file__)),
                        '../../../nosetests.cfg')
    argv = [sys.argv[0], '-c', setupcfg, ] + sys.argv[1:]

    nose.main(defaultTest='goodscloud_api_client', argv=argv)
