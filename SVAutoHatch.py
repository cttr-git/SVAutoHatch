#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import ImageProcPythonCommand
from Commands.Keys import Button, Direction
import tkinter as tk
import datetime
import cv2


class SVAutoHatch(ImageProcPythonCommand):
    NAME = '【SV】自動孵化【_cttr】'

    def __init__(self, cam, gui=None):
        '''
        コンストラクタ
        初期設定を行います
        '''
        super().__init__(cam)
        self.cam = cam
        self.gui = gui
        # 動作確認用(通常時はFalse、Trueにすると様々なログ出力が増えます)
        self.debug_mode = False
        # 調理移動量(環境によって0.4~0.6程度で調整)
        self.duration_base = 0.5
        # 動作安定化(各waitの待ち時間に追加する)
        self.add_time = 0
        # そらをとぶモード(その場: 1、調整: 2)
        # 1を選ぶ場合は一度そらをとぶでゼロゲートに飛んでから開始してください
        self.fly_mode = 1
        # 孵化BOX数
        self.box_cnt = None
        # 手持ち空き数
        self.poke_cnt = None
        # 孵化時間
        self.hatch_time = 400
        # 画像フォルダパス
        self.base_img_path = "SVAutoHatch/"

    def do(self):
        '''
        メイン関数
        '''
        # 孵化BOX数をGUIから指定する
        self.gui_window_generate(
            size='280x80', title='孵化BOX数指定', label='整数で指定してください', func='box_cnt_decision')

        # 最初に手持ちを確認して一回に孵化させる数を決める
        self.select_main_menu('box')
        self.check_free_space_on_hand()
        # ポケモンを入れ替える前のため入れ替え後の数に調整する
        self.poke_cnt += 1
        self.press(Button.B, duration=0.1, wait=4+self.add_time)
        self.press(Button.B, duration=0.1, wait=0.5+self.add_time)

        print('GUIで孵化BOX数を整数で指定してください')
        while(1):
            # waitは負荷軽減対応
            self.wait(1+self.add_time)
            if self.box_cnt is not None:
                break
        print(f'{self.box_cnt} BOX分孵化を開始します')

        # GUIで指定された回数処理する
        for i in range(1, self.box_cnt+1):
            print(f'進捗 {i}/{self.box_cnt} BOX')
            # ゼロゲート判定/方向を調整
            self.adjustment_position()
            # ピクニック可能位置まで移動
            self.press(Direction.UP, duration=2, wait=0.5+self.add_time)
            # サンドイッチを作る
            self.make_sandwich()
            # タマゴを受け取る
            self.get_egg(self.poke_cnt*6)
            # 孵化
            self.hatch_egg(i+1)

    def make_sandwich(self):
        '''
        サンドイッチ(スーパーピーナッツバターサンド)作成
        '''
        print('make_sandwich start') if self.debug_mode else ''
        # メインメニューでピクニックを選択する
        self.select_main_menu('picnic')

        # ピクニック開始待ち
        print('ピクニック開始待ち') if self.debug_mode else ''
        self.wait(10+self.add_time)
        self.press(Direction.UP, duration=2, wait=0.5+self.add_time)
        self.press(Button.A, duration=0.1, wait=1+self.add_time)
        # ピニックセットを認識
        if not self.isContainTemplate(template_path=self.base_img_path+"picnicset.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
            self.recovery()
            self.make_sandwich()
            return

        print('ピニックセットを認識') if self.debug_mode else ''
        self.press(Button.A, duration=0.1, wait=5+self.add_time)

        # サンドウィッチ選択
        while(1):
            # 対象に合うまで1つずつカーソルを右にずらす
            if self.isContainTemplate(template_path=self.base_img_path+"super_peanut_butter_sandwich.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
                self.press(Button.A, duration=0.1, wait=0.5+self.add_time)
                self.press(Button.A, duration=0.1, wait=0.5+self.add_time)
                break
            else:
                self.press(Direction.RIGHT, duration=0.1,
                           wait=0.3+self.add_time)

        # クッキング開始待ち
        while(1):
            self.wait(1+self.add_time)
            if self.isContainTemplate(template_path=self.base_img_path+"cooking_start.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
                print('調理開始') if self.debug_mode else ''
                break

        self.wait(1+self.add_time)
        # 1枚目を置く
        self.press(Direction.UP, duration=self.duration_base +
                   0.05, wait=0.5+self.add_time)
        self.hold(Button.A, wait=0.5+self.add_time)
        self.press(Direction.DOWN, duration=self.duration_base,
                   wait=0.5+self.add_time)
        if not self.isContainTemplate(template_path=self.base_img_path+"bananaslice.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
            print('食材を掴めませんでした')
            print('err_code: E0005')
            self.get_screenshot('E0005')
        self.holdEnd(Button.A)
        # 2枚目を置く
        self.press(Direction.UP, duration=self.duration_base,
                   wait=0.5+self.add_time)
        self.hold(Button.A, wait=0.5+self.add_time)
        self.press(Direction.DOWN, duration=self.duration_base,
                   wait=0.5+self.add_time)
        if not self.isContainTemplate(template_path=self.base_img_path+"bananaslice.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
            print('食材を掴めませんでした')
            print('err_code: E0006')
            self.get_screenshot('E0006')
        self.holdEnd(Button.A)
        # 3枚目を置く
        self.press(Direction.UP, duration=self.duration_base,
                   wait=0.5+self.add_time)
        self.hold(Button.A, wait=0.5+self.add_time)
        self.press(Direction.DOWN, duration=self.duration_base,
                   wait=0.5+self.add_time)
        self.press(Direction.LEFT, duration=0.2, wait=0.5+self.add_time)
        if not self.isContainTemplate(template_path=self.base_img_path+"bananaslice.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
            print('食材を掴めませんでした')
            print('err_code: E0007')
            self.get_screenshot('E0007')
        self.holdEnd(Button.A)
        self.wait(3+self.add_time)
        # パンを捨てる
        self.press(Direction.UP, duration=2, wait=0.5+self.add_time)
        self.press(Button.A, duration=0.1, wait=0.5+self.add_time)
        self.wait(2+self.add_time)
        # ピンを刺す
        self.press(Button.A, duration=0.1, wait=0.5+self.add_time)

        print("完成")

        self.wait(10+self.add_time)
        self.press(Button.A, duration=0.1, wait=0.5+self.add_time)
        self.wait(30+self.add_time)
        self.press(Button.A, duration=0.1, wait=0.5+self.add_time)

    def get_egg(self, receive: int):
        '''
        タマゴ受け取り

        Parameters
            receive: 最大タマゴ受け取り数
        '''
        print('get_egg start') if self.debug_mode else ''
        # 移動安定のためにしゃがむ
        self.press(Button.B, duration=0.1, wait=1+self.add_time)
        # 左へ
        self.press(Direction.LEFT, duration=0.1, wait=1+self.add_time)
        self.press(Button.L, duration=0.1, wait=1+self.add_time)
        self.press(Direction.UP, duration=0.3, wait=1+self.add_time)
        # 右へ
        self.press(Direction.RIGHT, duration=0.1, wait=1+self.add_time)
        self.press(Button.L, duration=0.1, wait=1+self.add_time)
        self.press(Direction.UP, duration=0.45, wait=1+self.add_time)
        # 右へ
        self.press(Direction.RIGHT, duration=0.1, wait=1+self.add_time)
        self.press(Button.L, duration=0.1, wait=1+self.add_time)
        self.press(Direction.UP, duration=0.15, wait=1+self.add_time)

        # タマゴ待ち
        receive_cnt = 0
        for i in range(1, 4):
            print('タマゴ待ち') if self.debug_mode else ''
            self.wait(receive/3+self.add_time)
            # 受け取り
            self.press(Button.A, duration=0.1, wait=1+self.add_time)
            if not self.isContainTemplate(template_path=self.base_img_path+"look.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                print('バスケットを確認できなかったため処理を中断します。')
                print('err_code: E0003')
                self.get_screenshot('E0003')
                self.finish()
            while(1):
                self.wait(0.5)
                # 1 のぞきこんだ！ Bボタン→2
                if self.isContainTemplate(template_path=self.base_img_path+"look.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
                # 2 入ってました！ Bボタン→3
                if self.isContainTemplate(template_path=self.base_img_path+"egg_in2.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
                # 3 引きとりますか？ Bボタン→4
                if self.isContainTemplate(template_path=self.base_img_path+"accept.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
                    # 4 はい/いいえ Aボタン→7, Bボタン→5
                    if receive > receive_cnt:
                        self.press(Button.A, duration=0.1,
                                   wait=0.5+self.add_time)
                    else:
                        self.press(Button.B, duration=0.1,
                                   wait=0.5+self.add_time)
                # 5 寄贈しますが よろしいですか？ Bボタン→6
                if self.isContainTemplate(template_path=self.base_img_path+"gift.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
                    # 6 はい/いいえ Aボタン→9, Bボタン→7
                    if receive <= receive_cnt:
                        self.press(Button.A, duration=0.1,
                                   wait=0.5+self.add_time)
                    else:
                        self.press(Button.B, duration=0.1,
                                   wait=0.5+self.add_time)
                # 7 引きとりました Bボタン→8
                if self.isContainTemplate(template_path=self.base_img_path+"accepting.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
                    receive_cnt += 1
                    print(
                        f'タマゴ受け取り {receive_cnt}/{receive} 個目') if self.debug_mode else ''
                # 8 入っているみたい！ Bボタン→2
                if self.isContainTemplate(template_path=self.base_img_path+"egg_in.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
                # 9 寄贈しました Bボタン→8
                if self.isContainTemplate(template_path=self.base_img_path+"gift2.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
                # バスケットの中が空になった
                if self.isContainTemplate(template_path=self.base_img_path+"no_egg.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    self.press(Button.B, duration=0.1,
                               wait=0.5+self.add_time)
                    print(f'バスケットの中身が空になりました') if self.debug_mode else ''
                    break

        print('ピクニック終了') if self.debug_mode else ''
        self.press(Button.Y, duration=0.1, wait=1+self.add_time)
        self.press(Button.A, duration=0.1, wait=5+self.add_time)
        self.press(Button.A, duration=0.1, wait=1+self.add_time)
        self.press(Button.L, duration=0.1, wait=0.5+self.add_time)

    def hatch_egg(self, next_box_cnt: int = 30):
        '''
        孵化

        Parameters
            next_box_cnt: 孵化するBOXの位置(初期値30)
        '''
        print('hatch_egg start') if self.debug_mode else ''
        self.wait(1+self.add_time)
        # BOXを開く
        self.select_main_menu('box')

        # 手持ち空き数に合わせて孵化用とほのおのからだポケモンを入れ替える
        for i in range(1, next_box_cnt):
            self.press(Button.L, duration=0.1, wait=0.5+self.add_time)
        if self.poke_cnt == 4:
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.LEFT, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.DOWN, duration=0.1)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.DOWN, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.RIGHT, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.UP, duration=0.1)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.UP, duration=0.1)
        elif self.poke_cnt == 5:
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.LEFT, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.DOWN, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.RIGHT, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
        else:
            pass

        # BOX選択
        print('BOX選択') if self.debug_mode else ''
        for i in range(1, next_box_cnt):
            self.press(Button.R, duration=0.1, wait=0.5+self.add_time)
        # 6列分処理
        for j in range(1, 7):
            # 次の列へ移動
            for i in range(j-1):
                self.press(Direction.RIGHT, duration=0.1,
                           wait=0.3+self.add_time)
            # 手持ち空き数に合わせてタマゴを選択
            if self.poke_cnt == 4:
                self.press(Button.MINUS, duration=0.1, wait=0.5+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Button.A, duration=0.1, wait=0.2+self.add_time)
            elif self.poke_cnt == 5:
                self.press(Button.MINUS, duration=0.1, wait=0.5+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Button.A, duration=0.1, wait=0.2+self.add_time)
            else:
                pass
            # 手持ちまで移動
            for i in range(j):
                self.press(Direction.LEFT, duration=0.1,
                           wait=0.2+self.add_time)
            # 手持ち空き数に合わせてタマゴを手持ちに加える
            if self.poke_cnt == 4:
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
            elif self.poke_cnt == 5:
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
            else:
                pass
            self.press(Button.A, duration=0.1, wait=0.2+self.add_time)
            # boxを閉じる
            self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
            self.wait(1+self.add_time)
            self.press(Button.B, duration=0.1, wait=4+self.add_time)

            print(f"孵化開始({j}/6セット目)")
            self.press(Button.PLUS, 0.1, wait=0.5+self.add_time)
            self.press(Direction.UP, duration=1.0, wait=0.5+self.add_time)
            # 孵化時間まで移動し続ける
            self.hold(Direction.LEFT)
            self.hold(Direction.R_LEFT)
            born_cnt = 0
            for i in range(0, self.hatch_time):
                self.press(Button.A, wait=0.5+self.add_time)
                if self.isContainTemplate(template_path=self.base_img_path+"born.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
                    born_cnt += 1
                    print(f'{born_cnt}匹孵化しました') if self.debug_mode else ''
                if born_cnt >= self.poke_cnt:
                    print('手持ちのタマゴを孵化し終えたため次のセットに移ります') if self.debug_mode else ''
                    self.press(Button.A, wait=2+self.add_time)
                    break
            self.holdEnd(Direction.LEFT)
            self.holdEnd(Direction.R_LEFT)
            print(f"孵化終了({j}/6セット目)")

            self.wait(1+self.add_time)
            self.press(Button.X, duration=0.1, wait=2+self.add_time)
            self.select_main_menu('box')
            # 手持ち空き数に合わせて手持ちの孵化したポケモンを選択
            if self.poke_cnt == 4:
                self.press(Direction.LEFT, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Button.MINUS, duration=0.1, wait=0.5+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Button.A, duration=0.1, wait=0.2+self.add_time)
                self.press(Direction.UP, duration=0.1, wait=0.2+self.add_time)
                self.press(Direction.UP, duration=0.1, wait=0.2+self.add_time)
            elif self.poke_cnt == 5:
                self.press(Direction.LEFT, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Button.MINUS, duration=0.1, wait=0.5+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Direction.DOWN, duration=0.1,
                           wait=0.2+self.add_time)
                self.press(Button.A, duration=0.1, wait=0.2+self.add_time)
                self.press(Direction.UP, duration=0.1, wait=0.2+self.add_time)
            else:
                pass
            # 次の列へ移動
            for i in range(j):
                self.press(Direction.RIGHT, duration=0.1,
                           wait=0.2+self.add_time)
            self.press(Button.A, duration=0.1, wait=0.5+self.add_time)
            self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
            self.wait(4+self.add_time)
            self.press(Button.B, duration=0.1, wait=0.5+self.add_time)

            # そらをとぶで位置リセット
            self.standing_position_reset()

            if not j == 6:
                # ゼロゲート判定/方向を調整
                self.adjustment_position()
                self.press(Direction.UP, duration=2, wait=1+self.add_time)

            self.press(Button.X, duration=0.1, wait=2+self.add_time)
            self.select_main_menu('box')

        # ポケモンをたまご回収用に入れ替える
        print("手持ちを卵回収用に入れ替えます")
        for i in range(1, next_box_cnt):
            self.press(Button.L, duration=0.1, wait=0.5+self.add_time)

        # 手持ち空き数に合わせて孵化用とほのおのからだポケモンを入れ替える
        if self.poke_cnt == 4:
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.LEFT, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.DOWN, duration=0.2, wait=1+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.RIGHT, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.LEFT, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.DOWN, duration=0.2, wait=1+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
        elif self.poke_cnt == 5:
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.LEFT, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.RIGHT, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
            self.press(Direction.LEFT, duration=0.1, wait=0.2+self.add_time)
            self.press(Button.Y, duration=0.1, wait=0.2+self.add_time)
        else:
            pass
        # 次タマゴを入れるBOXに合わせて閉じる
        for i in range(1, next_box_cnt+1):
            self.press(Button.R, duration=0.1, wait=0.5+self.add_time)
        self.press(Button.B, duration=0.1, wait=0.5+self.add_time)
        self.wait(4+self.add_time)
        self.press(Direction.DOWN, duration=0.1, wait=0.5+self.add_time)
        self.press(Button.B, duration=0.1, wait=0.5+self.add_time)

    def check_free_space_on_hand(self):
        '''
        手持ち空きポケモン数を確認
        '''
        print('check_free_space_on_hand start') if self.debug_mode else ''
        if self.isContainTemplate(template_path=self.base_img_path+"free_space_on_hand3.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
            self.poke_cnt = 3
        if self.isContainTemplate(template_path=self.base_img_path+"free_space_on_hand4.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
            self.poke_cnt = 4
        if self.isContainTemplate(template_path=self.base_img_path+"free_space_on_hand5.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
            self.poke_cnt = 5
        if self.poke_cnt is None:
            print('処理に必要な手持ち空き数が判断できなかったため処理を中断します')
            print('err_code: E0002')
            self.get_screenshot('E0002')
            self.finish()
        print(f'現在の手持ち空き数: {self.poke_cnt}') if self.debug_mode else ''

    def select_main_menu(self, menu_name: str):
        '''
        メインメニューで指定のメニューを選択して開く

        Parameters
            menu_name: メニュー画像名(拡張子を除く)
        '''
        print('select_main_menu start') if self.debug_mode else ''
        self.wait(2)
        mc_result = self.detect_circular_minimap(
            search_range=[494, 720, 1050, 1280], circle_radius=80,  return_info=False)
        if mc_result:
            self.press(Button.X, duration=0.1, wait=2+self.add_time)
            self.select_main_menu(menu_name)
            return

        if self.isContainTemplate(template_path=self.base_img_path+"main_menu.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
            self.press(Direction.RIGHT, duration=0.1, wait=0.3+self.add_time)
            while(1):
                if self.isContainTemplate(template_path=self.base_img_path+menu_name+".png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
                    self.press(Button.A, duration=0.1, wait=5+self.add_time)
                    # うまく反応しない場合があるのでもうメインメニューが表示されていたら一度呼び出してリカバリー
                    if self.isContainTemplate(template_path=self.base_img_path+"main_menu.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
                        self.select_main_menu(menu_name)
                    break
                else:
                    self.press(Direction.DOWN, duration=0.1,
                               wait=0.5+self.add_time)
        else:
            print('メインメニューが検出できなかったため処理を中断します')
            print('err_code: E0004')
            self.get_screenshot('E0004')
            self.finish()

    def adjustment_position(self):
        '''
        立ち位置、方角を調整
        '''
        print('adjustment_position start') if self.debug_mode else ''
        if self.isContainTemplate(template_path=self.base_img_path+"east_direction.png", threshold=0.8, use_gray=False, show_value=self.debug_mode):
            print('ゼロゲート(地上)、東向きを認識しました。') if self.debug_mode else ''
            self.press(Direction.DOWN_LEFT, duration=0.1,
                       wait=0.5+self.add_time)
            self.press(Button.L, duration=0.1, wait=0.5+self.add_time)
        elif self.isContainTemplate(template_path=self.base_img_path+"south_direction.png", threshold=0.8, use_gray=False, show_value=self.debug_mode):
            print('ゼロゲート(地上)、南向きを認識しました。') if self.debug_mode else ''
            self.press(Direction.DOWN_RIGHT, duration=0.1,
                       wait=0.5+self.add_time)
            self.press(Button.L, duration=0.1, wait=0.5+self.add_time)
        elif self.isContainTemplate(template_path=self.base_img_path+"west_direction.png", threshold=0.8, use_gray=False, show_value=self.debug_mode):
            print('ゼロゲート(地上)、西向きを認識しました。') if self.debug_mode else ''
            self.press(Direction.UP_RIGHT, duration=0.1,
                       wait=0.5+self.add_time)
            self.press(Button.L, duration=0.1, wait=0.5+self.add_time)
        elif self.isContainTemplate(template_path=self.base_img_path+"north_direction.png", threshold=0.8, use_gray=False, show_value=self.debug_mode):
            print('ゼロゲート(地上)、北向きを認識しました。') if self.debug_mode else ''
            self.press(Direction.UP_LEFT, duration=0.1,
                       wait=0.5+self.add_time)
            self.press(Button.L, duration=0.1, wait=0.5+self.add_time)
        else:
            print('立ち位置と方角の調整に失敗したため処理を中断します。')
            print('err_code: E0001')
            self.get_screenshot('E0001')
            self.finish()

    def standing_position_reset(self):
        print('standing_position_reset start') if self.debug_mode else ''
        '''
        そらを飛ぶで立ち位置をリセット
        '''
        self.press(Button.Y, duration=0.1, wait=3+self.add_time)
        self.press(Button.ZL, duration=0.1, wait=1+self.add_time)
        if self.fly_mode == 1:
            # そらをとぶ
            for i in range(30):
                self.press(Button.A, duration=0.1, wait=1+self.add_time)
                if self.isContainTemplate(template_path=self.base_img_path+"fly.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
                    print('そらをとぶを認識しました') if self.debug_mode else ''
                    self.press(Button.A, duration=0.1, wait=2+self.add_time)
                    self.press(Button.A, duration=0.1, wait=5+self.add_time)
                    return
        elif self.fly_mode == 2:
            # 位置調整準備
            if self.isContainTemplate(template_path=self.base_img_path+"map_r.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
                self.press(Button.R, duration=0.1, wait=0.5+self.add_time)
            # ゼロゲートを見つけるまで位置調整
            for i in range(30):
                # そらをとぶ
                if self.isContainTemplate(template_path=self.base_img_path+"fly.png", threshold=0.9, use_gray=False, show_value=self.debug_mode):
                    print('そらをとぶを認識しました') if self.debug_mode else ''
                    self.press(Button.A, duration=0.1, wait=2+self.add_time)
                    self.press(Button.A, duration=0.1, wait=10+self.add_time)
                    return
                # 位置調整
                self.press(Direction.DOWN, duration=0.1, wait=1+self.add_time)
                self.press(Direction.UP, duration=0.1, wait=1+self.add_time)
                # ピンの位置確認
                if self.isContainTemplate(template_path=self.base_img_path+"pin1.png", threshold=0.8, use_gray=False, show_value=self.debug_mode) or self.isContainTemplate(template_path=self.base_img_path+"pin2.png", threshold=0.8, use_gray=False, show_value=self.debug_mode):
                    self.press(Button.A, duration=0.1, wait=0.2+self.add_time)
        else:
            print('そらをとぶモードが規定外の設定を検出しました、処理を中断します。') if self.debug_mode else ''
            self.get_screenshot('E0008')
            self.finish()

    def recovery(self):
        print('recovery start') if self.debug_mode else ''
        '''
        メインメニューを閉じた状態までリカバリー
        '''
        for i in range(0, 10):
            self.press(Button.B, wait=0.2+self.add_time)

        # ピクニック中
        if self.isContainTemplate(template_path=self.base_img_path+"picnic_end.png", threshold=0.9, use_gray=True, show_value=self.debug_mode):
            self.press(Button.Y, wait=0.5+self.add_time)
            self.press(Button.A, wait=0.5+self.add_time)
            # そらをとぶで位置リセット
            self.standing_position_reset()

    def get_screenshot(self, filename):
        print('get_screenshot start') if self.debug_mode else ''
        '''
        スクリーンショット保存
        /SerialController/Captures/SVAutoHatch/ に保存されます

        Parameters
            filename: ファイル名
        '''
        img_path = 'SVAutoHatch/'
        d = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.camera.saveCapture(f'{img_path}{filename}_{d}')

    def gui_window_generate(self, size: str, title: str, label: str, func: str):
        '''
        GUI入力画面生成

        Parameters
            size: GUIサイズ
            title: GUI名
            lable: 説明文
            func: ボタン押下時に呼び出す関数
        '''
        print('gui_window_generate start') if self.debug_mode else ''
        # 入力画面
        self.Window = tk.Toplevel()
        self.Window.geometry(size)
        self.Window.title(title)
        self.frame = tk.Frame(self.Window)
        self.frame.pack()
        # ボタン
        self.label = tk.Label(self.frame, text=label)
        self.entry = tk.Entry(self.frame)
        if func == 'box_cnt_decision':
            self.button = tk.Button(
                self.frame, text='決定', command=self.box_cnt_decision)
        else:
            pass
        self.entry.pack()
        self.label.pack()
        self.button.pack()

    def box_cnt_decision(self):
        '''
        BOX数決定
        '''
        print('box_cnt_decision start') if self.debug_mode else ''
        try:
            input = self.entry.get()
            self.box_cnt = int(input) if not input == '' else 1
        except ValueError:
            self.box_cnt = 1
        self.Window.destroy()

    def detect_circular_minimap(self, search_range: list = [0, 720, 0, 1280], circle_radius: int = 80, return_info: bool = False):
        '''
        ミニマップの円形を検出する

        Parameters
            search_range: ファイル名
            circle_radius: 円の半径
            return_info: 検出結果として円の情報を受取る場合はTrue、検出結果をbool値で受け取るならFalse
        '''
        # 映像を読み込む
        cap = self.camera.readFrame()
        # グレースケール変換 (白・灰色・黒色で構成されている画像)
        cap = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
        # 対象の範囲をトリミング
        img = cap[search_range[0]:search_range[1],
                  search_range[2]:search_range[3]]
        # 円検出
        circles = None
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                   param1=100, param2=60, minRadius=circle_radius, maxRadius=0)
        # 円が見つからなかった場合の処理
        if circles is None:
            return (0, 0, 0) if return_info else False
        # 検出した円の半径とcircle_radiusを比較
        if circles[0][0][2] > circle_radius:
            print('ミニマップを検出しました') if self.debug_mode else ''
            return (circles[0][0][0], circles[0][0][1], circles[0][0][2]) if return_info else True
        else:
            return (0, 0, 0) if return_info else False
