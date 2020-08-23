from time import sleep
from tkinter import Tk, Canvas, PhotoImage, Frame, Button, Label
from tkinter.constants import *
from sys import exit
from math import floor, ceil, pow
import PIL.ImageTk
import PIL.Image
import PIL.ImageDraw
from win32api import GetCursorPos,GetSystemMetrics
from copy import deepcopy

#数据和信息
from data import *
#图片预导入
##背景贴图
bgimg = PIL.Image.open('textures/itembg.png').resize((64,64), PIL.Image.NEAREST)
m1img = PIL.Image.open('textures/m1.png').resize((64,64), PIL.Image.NEAREST)
m2img = PIL.Image.open('textures/m2.png').resize((64,64), PIL.Image.NEAREST)
coolantimg = PIL.Image.open('textures/coolant.png').resize((64,64), PIL.Image.NEAREST)
core1x1topimg = PIL.Image.open('textures/core1x1top.png')
core2x2top_partimg = PIL.Image.open('textures/core2x2top_part.png')
startimg = PIL.Image.open('textures/start.png').resize((128,64), PIL.Image.NEAREST)
stopimg = PIL.Image.open('textures/stop.png').resize((128,64), PIL.Image.NEAREST)
pauseimg = PIL.Image.open('textures/pause.png').resize((128,64), PIL.Image.NEAREST)
resetimg = PIL.Image.open('textures/reset.png').resize((128,64), PIL.Image.NEAREST)
time_linesimg = PIL.Image.open('textures/time_lines.png')
selectedimg = PIL.Image.open('textures/selected.png').resize((40,40), PIL.Image.NEAREST)
##燃料棒图片
rodkeys = list(all_rods.keys())
for rod_id in rodkeys:
    exec('{0}img = PIL.Image.open(\'textures/{1}.png\').resize((64,64), PIL.Image.NEAREST)'.format(rod_id, all_rods[rod_id]['tex_name']))
    exec('{0}topimg = PIL.Image.open(\'textures/{1}top.png\')'.format(rod_id, all_rods[rod_id]['tex_name']))
    exec('{0}top_closeimg = PIL.Image.open(\'textures/{1}top_close.png\')'.format(rod_id, all_rods[rod_id]['tex_name']))
##冷却液图片
coolantkeys = list(all_coolant.keys())
for coolant_id in coolantkeys:
    exec('{0}img = PIL.Image.open(\'textures/{0}.png\').resize((64,64), PIL.Image.NEAREST)'.format(coolant_id))

##工具图片
core1x1img = PIL.Image.open('textures/core1x1.png').resize((64,64), PIL.Image.NEAREST)
core2x2img = PIL.Image.open('textures/core2x2.png').resize((64,64), PIL.Image.NEAREST)
wrenchimg = PIL.Image.open('textures/wrench.png').resize((64,64), PIL.Image.NEAREST)
pliersimg = PIL.Image.open('textures/pliers.png').resize((64,64), PIL.Image.NEAREST)
soft_hammerimg = PIL.Image.open('textures/soft_hammer.png').resize((64,64), PIL.Image.NEAREST)

##显示设置贴图
dis_namesimg = PIL.Image.open('textures/dis_names.png').resize((40,40), PIL.Image.NEAREST)
dis_heatimg = PIL.Image.open('textures/dis_heat.png').resize((40,40), PIL.Image.NEAREST)
dis_neutronimg = PIL.Image.open('textures/dis_neutron.png').resize((40,40), PIL.Image.NEAREST)
dis_fluidimg = PIL.Image.open('textures/dis_fluid.png').resize((40,40), PIL.Image.NEAREST)
dis_moderateimg = PIL.Image.open('textures/dis_moderate.png').resize((40,40), PIL.Image.NEAREST)
dis_utilizationimg = PIL.Image.open('textures/dis_utilization.png').resize((40,40), PIL.Image.NEAREST)
dis_progressimg = PIL.Image.open('textures/dis_progress.png').resize((40,40), PIL.Image.NEAREST)

def close_window():
    exit()

###############################################
class main:
    def __init__(self):
        self.core_num = 4
        core_size = 600/self.core_num
        #字典
        self.mouse_setting = \
            {'m1' : 'core1x1',
             'm2' : 'wrench',
             'coolant':'industrial_coolant'}
        self.cores_setting = {'ttheat': 0, 'tttime':0,'core_num':self.core_num,'heat':0,
                              'fluid':{'industrial_coolant':None,
                                       'molten_lithium_chlorid':None,
                                       'molten_thorium_salt':None,
                                       'carbon_dioxide':None,
                                       'helium':None,
                                       'distill_water':None,
                                       'D2O_water':None,
                                       'HDO_water':None,
                                       'T2O_water':None,
                                       'molten_tin':None,
                                       'molten_sodium':None}}
        for i in range(self.core_num):
            for j in range(self.core_num):
                core_id = 'core{}_{}'.format(i,j)
                self.reset_core_setting(core_id)
        self.display_setting = \
            {'names'      : True,
             'heat'       : True,
             'neutron'    : True,
             'fluid'      : False,
             'moderate'   : False,
             'utilization': False,
             'progress'   : False}
        self.timegraph_setting = \
            {'max_heat' : 1000,
             'max_time' : 600}

        self.simwin = Tk()
        self.simwin.title('nuclearSimulator-{}'.format(version))
        self.simwin.iconbitmap('textures/nuclearsim.ico') 
        self.simwin.geometry('1560x680')
        self.simwin["background"] = '#aaaaaa'
        self.simwin.resizable(width=False, height=False)
        self.simwin.protocol('WM_DELETE_WINDOW', close_window)

        self.simwin.bind_all('<Alt-Key-h>',self.functionAdaptor(self.debug))
        self.simwin.focus_set()

        #显示模式部分
        self.dismode_frame = Frame(self.simwin, width=450, height=50, bg='#aaaaaa', highlightthickness=1, highlightbackground='#101010')
        self.dismode_frame.grid(row=0, column=0, padx=5, pady=2)
        ##循环全部
        display_keys = list(self.display_setting.keys())
        i = 0
        for dis_key in display_keys:
            exec('self.dis_{0}_b = Button(self.dismode_frame, command=self.functionAdaptor_b(self.set_display_setting, dis_id=dis_key), highlightthickness=0,bg=\'#aaaaaa\',activebackground=\'#aaaaaa\')'.format(dis_key))
            exec('self.dis_{0}_b.grid(row=0, column={1}, padx=5, pady=2)'.format(dis_key,i))
            exec('self.dis_{0}_b.bind(\'<Enter>\',self.functionAdaptor(self.Balloon_show, msg=infomation[dis_key]))'.format(dis_key))
            exec('self.dis_{0}_b.bind(\'<Leave>\',self.Balloon_destroy)'.format(dis_key))
            i += 1
        self.draw_dismode()

        #设置部分
        self.setting_frame = Frame(self.simwin, width=200, height=50, bg='#aaaaaa', highlightthickness=1, highlightbackground='#101010')
        self.setting_frame.grid(row=0, column=1, padx=5, pady=5)
        self.addsize_b = Button(self.setting_frame, text='+', font=font_button, bg='#aaaaaa',activebackground='#aaaaaa', width=2, height=1, command=lambda:self.add_core_num())
        self.addsize_b.pack(side=LEFT, padx=5, pady=5)
        self.addsize_b.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['addsize']))
        self.addsize_b.bind('<Leave>',self.Balloon_destroy)
        self.redsize_b = Button(self.setting_frame, text='-', font=font_button, bg='#aaaaaa',activebackground='#aaaaaa', width=2, height=1, command=lambda:self.reduce_core_num())
        self.redsize_b.pack(side=LEFT, padx=5, pady=5)
        self.redsize_b.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['redsize']))
        self.redsize_b.bind('<Leave>',self.Balloon_destroy)

        #燃料棒部分
        self.rod_frame = Frame(self.simwin, width=300, height=590, bg='#aaaaaa', highlightthickness=1, highlightbackground='#101010')
        self.rod_frame.grid(row=0, column=2, rowspan=2, padx=5, pady=5)
        ##燃料棒
        self.rodkeys = list(all_rods.keys())
        col_num = 4
        i,j = 0,0
        for rod_id in self.rodkeys:
            ###绘图
            exec('self.{0} = Canvas(self.rod_frame, width=64, height=64, bg=\'#aaaaaa\', highlightthickness=0)'.format(rod_id))
            exec('{0}Tex = PIL.Image.alpha_composite(bgimg, {0}img)'.format(rod_id))
            exec('{0}TexTk = PIL.ImageTk.PhotoImage({0}Tex)'.format(rod_id))
            exec('self.{0}_image=self.{0}.create_image(0, 0, anchor=NW, image={0}TexTk)'.format(rod_id))
            exec('self.{0}TexTk = {0}TexTk'.format(rod_id)) # keep img not be deleted
            exec('self.{0}.grid(row={1}, column={2}, padx=2, pady=2)'.format(rod_id, i,j))
            if j < col_num-1:
                j += 1
            else:
                j = 0
                i += 1
            ###添加触发
            self.set_rod_inf(rod_id)
            exec('self.{0}.bind(\'<Leave>\',self.Balloon_destroy)'.format(rod_id))
            exec('self.{0}.bind(\'<Button-1>\',self.functionAdaptor(self.set_mouse1, setting=rod_id))'.format(rod_id))
            exec('self.{0}.bind(\'<Button-3>\',self.functionAdaptor(self.set_mouse2, setting=rod_id))'.format(rod_id))

        #冷却液部分
        self.coolant_frame = Frame(self.simwin, width=300, height=200, bg='#aaaaaa', highlightthickness=1, highlightbackground='#101010')
        self.coolant_frame.grid(row=2, column=2, padx=5, pady=5)
        ##冷却液
        self.coolantkeys = list(all_coolant.keys())
        col_num = 4
        i,j = 0,0
        for coolant_id in self.coolantkeys:
            ###绘图
            exec('self.{0} = Canvas(self.coolant_frame, width=64, height=64, bg=\'#aaaaaa\', highlightthickness=0)'.format(coolant_id))
            exec('{0}Tex = PIL.Image.alpha_composite(bgimg, {0}img)'.format(coolant_id))
            exec('{0}TexTk = PIL.ImageTk.PhotoImage({0}Tex)'.format(coolant_id))
            exec('self.{0}_image=self.{0}.create_image(0, 0, anchor=NW, image={0}TexTk)'.format(coolant_id))
            exec('self.{0}TexTk = {0}TexTk'.format(coolant_id)) # keep img not be deleted
            exec('self.{0}.grid(row={1}, column={2}, padx=2, pady=2)'.format(coolant_id, i,j))
            if j < col_num-1:
                j += 1
            else:
                j = 0
                i += 1
            ###添加触发
            exec('self.{0}.bind(\'<Enter>\',self.functionAdaptor(self.Balloon_show, msg=infomation[coolant_id]))'.format(coolant_id))
            exec('self.{0}.bind(\'<Leave>\',self.Balloon_destroy)'.format(coolant_id))
            exec('self.{0}.bind(\'<Button-1>\',self.functionAdaptor(self.set_coolant, setting=coolant_id))'.format(coolant_id))

        #工具部分
        self.tool_frame = Frame(self.simwin, width=380, height=70, bg='#aaaaaa', highlightthickness=1, highlightbackground='#101010')
        self.tool_frame.grid(row=3, column=2, padx=5, pady=5)
        ##1x1反应室
        ###绘图
        self.core1x1 = Canvas(self.tool_frame, width=64, height=64, bg='#aaaaaa', highlightthickness=0)
        core1x1Tex = PIL.Image.alpha_composite(bgimg, core1x1img)
        core1x1TexTk = PIL.ImageTk.PhotoImage(core1x1Tex)
        self.core1x1_image=self.core1x1.create_image(0, 0, anchor=NW, image=core1x1TexTk)
        self.core1x1TexTk = core1x1TexTk # keep img not be deleted
        self.core1x1.pack(side=LEFT, padx=2, pady=2)
        ###添加触发
        self.core1x1.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['core1x1']))
        self.core1x1.bind('<Leave>',self.Balloon_destroy)
        self.core1x1.bind('<Button-1>',self.functionAdaptor(self.set_mouse1, setting='core1x1'))
        self.core1x1.bind('<Button-3>',self.functionAdaptor(self.set_mouse2, setting='core1x1'))
        ##2x2反应室
        ###绘图
        self.core2x2 = Canvas(self.tool_frame, width=64, height=64, bg='#aaaaaa', highlightthickness=0)
        core2x2Tex = PIL.Image.alpha_composite(bgimg, core2x2img)
        core2x2TexTk = PIL.ImageTk.PhotoImage(core2x2Tex)
        self.core2x2_image=self.core2x2.create_image(0, 0, anchor=NW, image=core2x2TexTk)
        self.core2x2TexTk = core2x2TexTk # keep img not be deleted
        self.core2x2.pack(side=LEFT, padx=2, pady=2)
        ###添加触发
        self.core2x2.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['core2x2']))
        self.core2x2.bind('<Leave>',self.Balloon_destroy)
        self.core2x2.bind('<Button-1>',self.functionAdaptor(self.set_mouse1, setting='core2x2'))
        self.core2x2.bind('<Button-3>',self.functionAdaptor(self.set_mouse2, setting='core2x2'))
        ##扳手
        ###绘图
        self.wrench = Canvas(self.tool_frame, width=64, height=64, bg='#aaaaaa', highlightthickness=0)
        wrenchTex = PIL.Image.alpha_composite(bgimg, wrenchimg)
        wrenchTexTk = PIL.ImageTk.PhotoImage(wrenchTex)
        self.wrench_image=self.wrench.create_image(0, 0, anchor=NW, image=wrenchTexTk)
        self.wrenchTexTk = wrenchTexTk # keep img not be deleted
        self.wrench.pack(side=LEFT, padx=2, pady=2)
        ###添加触发
        self.wrench.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['wrench']))
        self.wrench.bind('<Leave>',self.Balloon_destroy)
        self.wrench.bind('<Button-1>',self.functionAdaptor(self.set_mouse1, setting='wrench'))
        self.wrench.bind('<Button-3>',self.functionAdaptor(self.set_mouse2, setting='wrench'))
        ##钳子
        ###绘图
        self.pliers = Canvas(self.tool_frame, width=64, height=64, bg='#aaaaaa', highlightthickness=0)
        pliersTex = PIL.Image.alpha_composite(bgimg, pliersimg)
        pliersTexTk = PIL.ImageTk.PhotoImage(pliersTex)
        self.pliers_image=self.pliers.create_image(0, 0, anchor=NW, image=pliersTexTk)
        self.pliersTexTk = pliersTexTk # keep img not be deleted
        self.pliers.pack(side=LEFT, padx=2, pady=2)
        ###添加触发
        self.pliers.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['pliers']))
        self.pliers.bind('<Leave>',self.Balloon_destroy)
        self.pliers.bind('<Button-1>',self.functionAdaptor(self.set_mouse1, setting='pliers'))
        self.pliers.bind('<Button-3>',self.functionAdaptor(self.set_mouse2, setting='pliers'))
        ##软锤
        ###绘图
        self.soft_hammer = Canvas(self.tool_frame, width=64, height=64, bg='#aaaaaa', highlightthickness=0)
        soft_hammerTex = PIL.Image.alpha_composite(bgimg, soft_hammerimg)
        soft_hammerTexTk = PIL.ImageTk.PhotoImage(soft_hammerTex)
        self.soft_hammer_image=self.soft_hammer.create_image(0, 0, anchor=NW, image=soft_hammerTexTk)
        self.soft_hammerTexTk = soft_hammerTexTk # keep img not be deleted
        self.soft_hammer.pack(side=LEFT, padx=2, pady=2)
        ###添加触发
        self.soft_hammer.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['soft_hammer']))
        self.soft_hammer.bind('<Leave>',self.Balloon_destroy)
        self.soft_hammer.bind('<Button-1>',self.functionAdaptor(self.set_mouse1, setting='soft_hammer'))
        self.soft_hammer.bind('<Button-3>',self.functionAdaptor(self.set_mouse2, setting='soft_hammer'))
        #绘制小部件
        self.draw_appand()

        #反应堆部分
        self.cores_frame = Frame(self.simwin, width=600, height=600, bg='#aaaaaa', highlightthickness=1, highlightbackground='#101010')
        self.cores_frame.grid(row=1, column=0,rowspan=3, columnspan=2, padx=5, pady=5)
        self.form_core()

        ######################
        self.tick = 0 
        self.input_tick = 0 #时间
        #开始模拟键
        self.is_start = False
        startTk = PIL.ImageTk.PhotoImage(startimg)
        self.start_b = Button(self.simwin, image=startTk, command=lambda:self.start_sim(input_tick=self.input_tick), highlightthickness=0, bg='#aaaaaa',activebackground='#aaaaaa',bd=4)
        self.startTk = startTk
        self.start_b.grid(row=3, column=5, padx=5, pady=5)
        ##触发
        self.start_b.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['start_b']))
        self.start_b.bind('<Leave>',self.Balloon_destroy)

        #暂停模拟键
        pauseTk = PIL.ImageTk.PhotoImage(pauseimg)
        self.pause_b = Button(self.simwin, image=pauseTk, command=lambda:self.pause_sim(), highlightthickness=0, bg='#aaaaaa',activebackground='#aaaaaa',bd=4)
        self.pauseTk = pauseTk

        #停止模拟键
        stopTk = PIL.ImageTk.PhotoImage(stopimg)
        self.stop_b = Button(self.simwin, image=stopTk, command=lambda:self.stop_sim(input_tick=self.input_tick), highlightthickness=0, bg='#aaaaaa',activebackground='#aaaaaa',bd=4)
        self.stopTk = stopTk
        self.stop_b.grid(row=3, column=4, padx=5, pady=5)
        ##触发
        self.stop_b.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['stop_b']))
        self.stop_b.bind('<Leave>',self.Balloon_destroy)

        #重置模拟键
        resetTk = PIL.ImageTk.PhotoImage(resetimg)
        self.reset_b = Button(self.simwin, image=resetTk, command=lambda:self.reset_sim(), highlightthickness=0, bg='#aaaaaa',activebackground='#aaaaaa',bd=4)
        self.resetTk = resetTk
        ##触发
        self.reset_b.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['reset_b']))
        self.reset_b.bind('<Leave>',self.Balloon_destroy)

        #时间轴
        self.time_graph = Canvas(self.simwin, width=580, height=300, bg='#ffffff', highlightthickness=0)
        time_linesTex = time_linesimg.resize((580,300), PIL.Image.NEAREST)
        time_linesTexTk = PIL.ImageTk.PhotoImage(time_linesTex)
        self.time_lines = self.time_graph.create_image(0, 0, anchor=NW, image=time_linesTexTk)
        self.time_linesTexTk = time_linesTexTk
        self.time_graph.grid(row=0, column=3, rowspan=2, columnspan=3, padx=5, pady=5)
        ##效率百分百横线
        self.u100line = self.time_graph.create_line(0,300/2,580,300/2,fill='#ff8888', dash=(4, 4))
        self.u100text = self.time_graph.create_text(7,300/2-2,text='', anchor=SW, font=font_normal,fill='#9e4545')
        ##选择时间线
        self.selline = self.time_graph.create_line(0,0,0,300,fill='#000000')
        self.seltext = self.time_graph.create_text(7,300/2-2,text='', anchor=SW, font=font_normal,fill='#9e4545')
        ##触发
        self.time_graph.bind('<Enter>',self.functionAdaptor(self.Balloon_show, msg=infomation['time_graph']))
        self.time_graph.bind('<Leave>',self.Balloon_destroy)
        self.time_graph.bind('<Button-1>',self.functionAdaptor(self.change_time))

        #数据统计
        self.data_frame = Frame(self.simwin, width=580, height=230, bg='#aaaaaa', highlightthickness=1, highlightbackground='#101010')
        self.data_frame.grid(row=2, column=3, columnspan=3, padx=5, pady=5, sticky=NW)
        self.data_frame0 = Frame(self.data_frame, width=200, height=200, bg='#aaaaaa')
        self.data_frame0.place(x=0, y=0, anchor=NW)
        self.data_frame1 = Frame(self.data_frame, width=200, height=200, bg='#aaaaaa')
        self.data_frame1.place(x=575, y=0, anchor=NE)
        self.data_frame2 = Frame(self.data_frame, width=200, height=30, bg='#aaaaaa')
        self.data_frame2.place(x=0, y=225, anchor=SW)
        ##总产热
        self.data_ttheat = Label(self.data_frame0, fg=None, bg='#aaaaaa', justify=LEFT, font=font_normal)
        self.data_ttheat.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        ##平均产热速率
        self.data_pheat = Label(self.data_frame0, fg=None, bg='#aaaaaa', justify=LEFT, font=font_normal)
        self.data_pheat.grid(row=1, column=0, padx=5, pady=5, sticky=NW)
        ##平均利用率
        self.data_utilization = Label(self.data_frame0, fg=None, bg='#aaaaaa', justify=LEFT, font=font_normal)
        self.data_utilization.grid(row=2, column=0, padx=5, pady=5, sticky=NW)
        ##已反应时间
        self.data_time = Label(self.data_frame2, fg=None, bg='#aaaaaa', justify=LEFT, font=font_normal)
        self.data_time.grid(row=0, column=0, padx=5, pady=5, sticky=NW)
        ##输出流体
        self.coolantkeys = list(all_coolant.keys())
        for coolant_id in self.coolantkeys:
            exec('self.fluid_{0} = Label(self.data_frame1, fg=None, bg=\'#aaaaaa\', justify=LEFT, font=font_small)'.format(coolant_id))

        self.max_heat = 0
        
        self.updeta_ttinf()

        #提示框
        self.balloon=Label(self.simwin,fg=None,bg='#c4c4c4',justify=LEFT, font=font_normal)

################################################
    #字典设置
    ##反应室
    def reset_core_setting(self, core_id):
        self.cores_setting[core_id] = \
            {'base': None,
             'rod': None,
             'core_inf':None,
             'heat':0,
             'coolant':None,
             'fluid':0}

    ##显示设置
    def set_display_setting(self, dis_id):
        if not self.is_start:
            self.display_setting[dis_id] = not self.display_setting[dis_id]
            self.draw_dismode_specific(dis_id)
            self.draw_all(reform=False, draw=False, dis=True)

    def draw_dismode_specific(self, dis_id):
        if self.display_setting[dis_id]:
            exec('dis_{0}Tex = PIL.Image.alpha_composite(dis_{0}img, selectedimg)'.format(dis_id))
        else:
            exec('dis_{0}Tex = dis_{0}img.copy()'.format(dis_id))
        exec('dis_{0}TexTk = PIL.ImageTk.PhotoImage(dis_{0}Tex)'.format(dis_id))
        exec('self.dis_{0}_b[\'image\'] = dis_{0}TexTk'.format(dis_id))
        exec('self.dis_{0}TexTk = dis_{0}TexTk'.format(dis_id))

    def draw_dismode(self):
        display_key_list = list(self.display_setting.keys())
        for dis_key in display_key_list:
            self.draw_dismode_specific(dis_key)


    ##燃料棒
    def set_core_rod(self, posijk, rod_id=None):
        #输入必须有效!!!
        i,j,k = posijk
        core_id = 'core{}_{}'.format(i,j)
        coolant = all_coolant[self.cores_setting[core_id]['coolant']]
        if rod_id == None:
            if k==-1: self.cores_setting[core_id]['rod'] = None
            else: self.cores_setting[core_id]['rod'][k] = None
        else:
            if k==-1:
                self.cores_setting[core_id]['rod'] = {'id':rod_id, 'active':True}
                rod_type = all_rods[rod_id]['type']
                if rod_type == 'fuel_rod':
                    self.cores_setting[core_id]['rod']['life']=round(all_rods[rod_id]['detail']['life']*coolant['life'])
                    self.cores_setting[core_id]['rod']['life_multi']=1
                    self.cores_setting[core_id]['rod']['depleted']=False
                    self.cores_setting[core_id]['rod']['neutron']=0
                    self.cores_setting[core_id]['rod']['get_neutron']=0
                    self.cores_setting[core_id]['rod']['get_neutron_moderated']=0
                    self.cores_setting[core_id]['rod']['moderated']=False
                    self.cores_setting[core_id]['rod']['overloaded']=False
                    self.cores_setting[core_id]['rod']['overloaded2']=False
                    self.cores_setting[core_id]['rod']['utilization_N']=0
                elif rod_type == 'breed_rod':
                    self.cores_setting[core_id]['rod']['needed']=all_rods[rod_id]['detail']['needed']
                    self.cores_setting[core_id]['rod']['neutron']=0
                    self.cores_setting[core_id]['rod']['get_neutron']=0
                    self.cores_setting[core_id]['rod']['get_neutron_moderated']=0
                    self.cores_setting[core_id]['rod']['truning_speed']=0
                elif rod_type == 'absorb_rod':
                    self.cores_setting[core_id]['rod']['neutron']=0
                    self.cores_setting[core_id]['rod']['get_neutron']=0
                    self.cores_setting[core_id]['rod']['get_neutron_moderated']=0
                elif rod_type == 'moderate_rod':
                    self.cores_setting[core_id]['rod']['multi']=0
                else: pass
            else:
                self.cores_setting[core_id]['rod'][k] = {'id':rod_id, 'active':True}
                rod_type = all_rods[rod_id]['type']
                if rod_type == 'fuel_rod':
                    self.cores_setting[core_id]['rod'][k]['life']=round(all_rods[rod_id]['detail']['life']*coolant['life'])
                    self.cores_setting[core_id]['rod'][k]['life_multi']=1
                    self.cores_setting[core_id]['rod'][k]['depleted']=False
                    self.cores_setting[core_id]['rod'][k]['neutron']=0
                    self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                    self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                    self.cores_setting[core_id]['rod'][k]['moderated']=False
                    self.cores_setting[core_id]['rod'][k]['overloaded']=False
                    self.cores_setting[core_id]['rod'][k]['overloaded2']=False
                    self.cores_setting[core_id]['rod'][k]['utilization_N']=0
                elif rod_type == 'breed_rod':
                    self.cores_setting[core_id]['rod'][k]['needed']=all_rods[rod_id]['detail']['needed']
                    self.cores_setting[core_id]['rod'][k]['neutron']=0
                    self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                    self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                    self.cores_setting[core_id]['rod'][k]['truning_speed']=0
                elif rod_type == 'absorb_rod':
                    self.cores_setting[core_id]['rod'][k]['neutron']=0
                    self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                    self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                elif rod_type == 'moderate_rod':
                    self.cores_setting[core_id]['rod'][k]['multi']=0
                else: pass

    def reset_core_rod(self, posijk, clrall=False):
        i,j,k = posijk
        core_id = 'core{}_{}'.format(i,j)
        if self.cores_setting[core_id]['base'] == 'core1x1':
            rod = self.cores_setting[core_id]['rod']
            if rod != None:
                if clrall: self.set_core_rod((i,j,-1), rod['id'])
                else:
                    rod_type = all_rods[rod['id']]['type']
                    if rod_type == 'fuel_rod':
                        self.cores_setting[core_id]['rod']['life_multi']=1
                        self.cores_setting[core_id]['rod']['neutron']=0
                        self.cores_setting[core_id]['rod']['get_neutron']=0
                        self.cores_setting[core_id]['rod']['get_neutron_moderated']=0
                        self.cores_setting[core_id]['rod']['moderated']=False
                        self.cores_setting[core_id]['rod']['overloaded']=False
                        self.cores_setting[core_id]['rod']['overloaded2']=False
                        self.cores_setting[core_id]['rod']['utilization_N']=0
                    elif rod_type == 'breed_rod':
                        self.cores_setting[core_id]['rod']['neutron']=0
                        self.cores_setting[core_id]['rod']['get_neutron']=0
                        self.cores_setting[core_id]['rod']['get_neutron_moderated']=0
                        self.cores_setting[core_id]['rod']['truning_speed']=0
                    elif rod_type == 'absorb_rod':
                        self.cores_setting[core_id]['rod']['neutron']=0
                        self.cores_setting[core_id]['rod']['get_neutron']=0
                        self.cores_setting[core_id]['rod']['get_neutron_moderated']=0
                    elif rod_type == 'moderate_rod':
                        self.cores_setting[core_id]['rod']['multi']=0
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            if k != -1:
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None:
                    if clrall: self.set_core_rod((i,j,k), rod['id'])
                    else:
                        rod_type = all_rods[rod['id']]['type']
                        if rod_type == 'fuel_rod':
                            self.cores_setting[core_id]['rod'][k]['life_multi']=1
                            self.cores_setting[core_id]['rod'][k]['neutron']=0
                            self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                            self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                            self.cores_setting[core_id]['rod'][k]['moderated']=False
                            self.cores_setting[core_id]['rod'][k]['overloaded']=False
                            self.cores_setting[core_id]['rod'][k]['overloaded2']=False
                            self.cores_setting[core_id]['rod'][k]['utilization_N']=0
                        elif rod_type == 'breed_rod':
                            self.cores_setting[core_id]['rod'][k]['neutron']=0
                            self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                            self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                            self.cores_setting[core_id]['rod'][k]['truning_speed']=0
                        elif rod_type == 'absorb_rod':
                            self.cores_setting[core_id]['rod'][k]['neutron']=0
                            self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                            self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                        elif rod_type == 'moderate_rod':
                            self.cores_setting[core_id]['rod'][k]['multi']=0
            else:
                for k in range(4):
                    rod = self.cores_setting[core_id]['rod'][k]
                    if rod != None:
                        if clrall: self.set_core_rod((i,j,k), rod['id'])
                        else:
                            rod_type = all_rods[rod['id']]['type']
                            if rod_type == 'fuel_rod':
                                self.cores_setting[core_id]['rod'][k]['life_multi']=1
                                self.cores_setting[core_id]['rod'][k]['neutron']=0
                                self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                                self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                                self.cores_setting[core_id]['rod'][k]['moderated']=False
                                self.cores_setting[core_id]['rod'][k]['overloaded']=False
                                self.cores_setting[core_id]['rod'][k]['overloaded2']=False
                                self.cores_setting[core_id]['rod'][k]['utilization_N']=0
                            elif rod_type == 'breed_rod':
                                self.cores_setting[core_id]['rod'][k]['neutron']=0
                                self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                                self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                                self.cores_setting[core_id]['rod'][k]['truning_speed']=0
                            elif rod_type == 'absorb_rod':
                                self.cores_setting[core_id]['rod'][k]['neutron']=0
                                self.cores_setting[core_id]['rod'][k]['get_neutron']=0
                                self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']=0
                            elif rod_type == 'moderate_rod':
                                self.cores_setting[core_id]['rod'][k]['multi']=0

    #工具设置
    def draw_appand(self, updateid=None):
        keylist = list(self.mouse_setting.keys())
        for key in keylist:
            tool_id = self.mouse_setting[key]
            if tool_id != None:
                exec('{0}Tex = PIL.Image.alpha_composite(bgimg, {0}img)'.format(tool_id))
                exec('{0}Tex = PIL.Image.alpha_composite({0}Tex, {1}img)'.format(tool_id, key))
                exec('{0}TexTk = PIL.ImageTk.PhotoImage({0}Tex)'.format(tool_id))
                exec('self.{0}.itemconfigure(self.{0}_image, image={0}TexTk)'.format(tool_id))
                exec('self.{0}TexTk = {0}TexTk'.format(tool_id)) # keep img not be deleted
        if updateid != None:
            exec('{0}Tex = PIL.Image.alpha_composite(bgimg, {0}img)'.format(updateid))
            exec('{0}TexTk = PIL.ImageTk.PhotoImage({0}Tex)'.format(updateid))
            exec('self.{0}.itemconfigure(self.{0}_image, image={0}TexTk)'.format(updateid))
            exec('self.{0}TexTk = {0}TexTk'.format(updateid)) # keep img not be deleted

    def set_mouse1(self,event, setting=str):
        if self.mouse_setting['m1'] != setting:
            updateid = None
            if self.mouse_setting['m2'] == setting:
                self.mouse_setting['m2'] = None
            if self.mouse_setting['m1'] != None:
                updateid = self.mouse_setting['m1']
            self.mouse_setting['m1'] = setting
            self.draw_appand(updateid)

    def set_mouse2(self,event, setting=str):
        if self.mouse_setting['m2'] != setting:
            updateid = None
            if self.mouse_setting['m1'] == setting:
                self.mouse_setting['m1'] = None
            if self.mouse_setting['m2'] != None:
                updateid = self.mouse_setting['m2']
            self.mouse_setting['m2'] = setting
            self.draw_appand(updateid)

    def set_coolant(self,event, setting=str):
        if self.mouse_setting['coolant'] != setting:
            updateid = None
            if self.mouse_setting['coolant'] != None:
                updateid = self.mouse_setting['coolant']
            self.mouse_setting['coolant'] = setting
            ###重设燃料棒信息
            self.rodkeys = list(all_rods.keys())
            for rod_id in self.rodkeys:
                self.set_rod_inf(rod_id)
            self.draw_appand(updateid)

    ##燃料棒信息
    def set_rod_inf(self, rod_id):
        rod_type = all_rods[rod_id]['type']
        coolant = all_coolant[self.mouse_setting['coolant']]
        if rod_type == 'fuel_rod':
            coolant_name = infomation[self.mouse_setting['coolant']+'_name']
            emission_num = round(all_rods[rod_id]['detail']['emission'] * coolant['emission'])
            self_num = round(all_rods[rod_id]['detail']['self'] * coolant['self'])
            maximum_num = round(all_rods[rod_id]['detail']['maximum'] * coolant['maximum'])
            exec('self.factor_num = round({})'.format(coolant['factor'].format(all_rods[rod_id]['detail']['factor'])))
            factor_num = self.factor_num
            life_num = round(all_rods[rod_id]['detail']['life'] * coolant['life'])
            coolant_rod = infomation[self.mouse_setting['coolant']+'_rod']
            message = infomation[rod_id]\
                .format(coolant_name, emission_num, self_num, maximum_num, '1/'+str(factor_num), life_num//60, coolant_rod)
        else:
            message = infomation[rod_id]
        exec('self.{0}.unbind(\'<Enter>\')'.format(rod_id))
        exec('self.{0}.bind(\'<Enter>\',self.functionAdaptor(self.Balloon_show, msg=message))'.format(rod_id))



    #提示框
    def Balloon_show(self,event,msg):
        if not self.is_start:
            try:
                self.balloon.place_forget()
            except:
                pass
            self.balloon['text']=msg
            if event.x_root-self.simwin.winfo_rootx()>self.balloon.winfo_width() or self.simwin.winfo_height()-event.y_root+self.simwin.winfo_rooty()>self.balloon.winfo_height():
                self.balloon.place(x=0,y=self.simwin.winfo_height(),anchor=SW)
            else:
                self.balloon.place(x=self.simwin.winfo_width(),y=self.simwin.winfo_height(),anchor=SE)

    def Balloon_destroy(self,event=None):
        if not self.is_start:
            try:
                self.balloon.place_forget()
            except:
                pass

    #改变尺寸
    def add_core_num(self):
        if not self.is_start:
            for i in range(self.core_num):
                for j in range(self.core_num):
                    exec('self.core{}_{}.destroy()'.format(i,j))
            self.core_num += 1
            self.cores_setting['core_num'] = self.core_num
            # 扩增字典
            for i in range(self.core_num):
                core_id = 'core{}_{}'.format(i,self.core_num-1)
                self.reset_core_setting(core_id)
            for j in range(self.core_num-1):
                core_id = 'core{}_{}'.format(self.core_num-1,j)
                self.reset_core_setting(core_id)
            self.form_core()

    def reduce_core_num(self):
        if self.core_num > 1 and (not self.is_start):
            # 检测字典
            NotNull = False
            for i in range(self.core_num):
                if self.cores_setting['core{}_{}'.format(i,self.core_num-1)]['base'] != None:
                    NotNull = True
            for j in range(self.core_num-1):
                if self.cores_setting['core{}_{}'.format(self.core_num-1,j)]['base'] != None:
                    NotNull = True
            if NotNull:
                pass
            else:
                # 缩减字典
                for i in range(self.core_num):
                    del self.cores_setting['core{}_{}'.format(i,self.core_num-1)]
                for j in range(self.core_num-1):
                    del self.cores_setting['core{}_{}'.format(self.core_num-1,j)]
                ####
                for i in range(self.core_num):
                    for j in range(self.core_num):
                        exec('self.core{}_{}.destroy()'.format(i,j))
                self.core_num -= 1
                self.cores_setting['core_num'] = self.core_num
                self.form_core()

    #反应堆部分
    def form_core(self):
        core_size = 600//self.core_num
        for i in range(self.core_num):
            for j in range(self.core_num):
                #构造基本结构
                exec('self.core{0}_{1} = Frame(self.cores_frame, bg=\'#aaaaaa\', width={2}, height={2}, highlightthickness=2, highlightbackground=\'#aaaaaa\')'.format(i,j, core_size))
                exec('self.core{0}_{1}.grid(row={0}, column={1})'.format(i,j))
                #绘制内部结构
                core_id = 'core{}_{}'.format(i,j)
                if self.cores_setting[core_id]['base'] == 'core2x2':
                    self.form_core_cell((i,j), True)
                else:
                    self.form_core_cell((i,j), False)
                #改变信息
                self.change_core_dis((i,j))
    
    def form_core_cell(self, posij, quarter=False):
        i, j = posij
        core_size = 600//self.core_num
        core_id = 'core{}_{}'.format(i,j)
        display_key_list = list(self.display_setting.keys())
        if quarter: # 构造是否是四分之一的
            for k in range(4):
                #绘图
                exec('self.{0}_cell{1} = Canvas(self.{0}, width={2}, height={2}, highlightthickness=0)'\
                    .format(core_id, k, core_size//2-2))
                exec('{0}_cell{1}Tex = core2x2top_partimg.resize(({2},{2}), PIL.Image.NEAREST)'\
                    .format(core_id, k, core_size//2-2))
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None:
                    if rod['active']: exec('rodTex_part = {0}topimg.crop((4,4,12,12))'.format(rod['id']))
                    else: exec('rodTex_part = {0}top_closeimg.crop((4,4,12,12))'.format(rod['id']))
                    exec('rodTex_part = rodTex_part.resize(({0},{0}), PIL.Image.NEAREST)'.format(core_size//2-2))
                    exec('{0}_cell{1}Tex = PIL.Image.alpha_composite({0}_cell{1}Tex, rodTex_part)'.format(core_id, k))
                exec('{0}_cell{1}TexTk = PIL.ImageTk.PhotoImage({0}_cell{1}Tex)'.format(core_id, k))
                exec('self.{0}_cell{1}_image=self.{0}_cell{1}.create_image(0,0,anchor=NW,image={0}_cell{1}TexTk)'.format(core_id, k))
                exec('self.{0}_cell{1}TexTk = {0}_cell{1}TexTk'.format(core_id, k)) # keep img not be deleted
                #信息
                self.form_core_dis((i,j,k), core_size)
                #添加触发
                exec('self.core{0}_{1}_cell{2}.bind(\'<Leave>\',self.Balloon_destroy)'.format(i,j,k))
                exec('self.core{0}_{1}_cell{2}.bind(\'<Button-1>\',self.functionAdaptor(self.click_core,posijk=({0},{1},{2})))'.format(i,j,k))
                exec('self.core{0}_{1}_cell{2}.bind(\'<Button-3>\',self.functionAdaptor(self.click_core,posijk=({0},{1},{2})))'.format(i,j,k))
                exec('self.core{0}_{1}_cell{2}.grid(row={3}, column={4})'.format(i,j,k,k//2,k%2))
                #提示框
                self.set_core_inf((i,j,k))
        else:
            if self.cores_setting[core_id]['base'] == 'core1x1':
                exec('self.{0}_cell0 = Canvas(self.{0}, width={1}, height={1}, highlightthickness=0)'\
                    .format(core_id, core_size-4))
                exec('{0}_cell0Tex = core1x1topimg.resize(({1},{1}), PIL.Image.NEAREST)'\
                    .format(core_id, core_size-4))
                rod = self.cores_setting[core_id]['rod']
                if rod != None:
                    if rod['active']: exec('rodTex = {0}topimg.resize(({1},{1}), PIL.Image.NEAREST)'.format(rod['id'], core_size-4))
                    else: exec('rodTex = {0}top_closeimg.resize(({1},{1}), PIL.Image.NEAREST)'.format(rod['id'], core_size-4))
                    exec('{0}_cell0Tex = PIL.Image.alpha_composite({0}_cell0Tex, rodTex)'.format(core_id))
                exec('{0}_cell0TexTk = PIL.ImageTk.PhotoImage({0}_cell0Tex)'.format(core_id))
                exec('self.{0}_cell0_image=self.{0}_cell0.create_image(0,0,anchor=NW,image={0}_cell0TexTk)'.format(core_id))
                exec('self.{0}_cell0TexTk = {0}_cell0TexTk'.format(core_id)) # keep img not be deleted

            elif self.cores_setting[core_id]['base'] == None:
                exec('self.{0}_cell0 = Canvas(self.{0}, width={1}, height={1}, highlightthickness=0)'.format(core_id, core_size-4))
                exec('{0}_cell0Tex = bgimg.resize(({1},{1}), PIL.Image.NEAREST)'.format(core_id, core_size-4))
                exec('{0}_cell0TexTk = PIL.ImageTk.PhotoImage({0}_cell0Tex)'.format(core_id))
                exec('self.{0}_cell0_image=self.{0}_cell0.create_image(0,0,anchor=NW,image={0}_cell0TexTk)'.format(core_id))
                exec('self.{0}_cell0TexTk = {0}_cell0TexTk'.format(core_id)) # keep img not be deleted
                
            #信息
            self.form_core_dis((i,j,-1), core_size)
            #添加触发
            exec('self.core{0}_{1}_cell0.bind(\'<Leave>\',self.Balloon_destroy)'.format(i,j))
            exec('self.core{0}_{1}_cell0.bind(\'<Button-1>\',self.functionAdaptor(self.click_core,posijk=({0},{1},-1)))'.format(i,j))
            exec('self.core{0}_{1}_cell0.bind(\'<Button-3>\',self.functionAdaptor(self.click_core,posijk=({0},{1},-1)))'.format(i,j))
            exec('self.core{0}_{1}_cell0.grid(row=0, column=0)'.format(i,j))
            #提示框
            self.set_core_inf((i,j,-1))

    #反应堆信息
    def set_core_inf(self, posijk):
        i,j,k = posijk
        core_id = 'core{}_{}'.format(i,j)
        if self.cores_setting[core_id]['base'] == None:
            self.cores_setting[core_id]['core_inf'] = None
            exec('self.core{0}_{1}_cell0.unbind(\'<Enter>\')'.format(i,j))
        elif self.cores_setting[core_id]['base'] == 'core1x1':
            rod = self.cores_setting[core_id]['rod']
            rod_inf = self.get_rod_inf(rod)
            self.cores_setting[core_id]['core_inf'] = '{1}{0}{0}{2}{0}{3}{0}{0}{4}{0}{5}'.format('\n',\
                infomation['core1x1_name'], infomation['core_com6'].format(self.cores_setting[core_id]['heat']),\
                infomation['core_com14'].format(infomation['{}_name'.format(self.cores_setting[core_id]['coolant'])]), rod_inf,\
                infomation['{}_core'.format(self.cores_setting[core_id]['coolant'])])
            message = self.cores_setting[core_id]['core_inf']
            exec('self.core{0}_{1}_cell0.unbind(\'<Enter>\')'.format(i,j))
            exec('self.core{0}_{1}_cell0.bind(\'<Enter>\',self.functionAdaptor(self.Balloon_show, msg=message))'.format(i,j))
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            rod = self.cores_setting[core_id]['rod'][k]
            rod_inf = self.get_rod_inf(rod)
            self.cores_setting[core_id]['core_inf'][k] = '{1}{0}{0}{2}{0}{3}{0}{0}{4}{0}{5}'.format('\n',\
                infomation['core2x2_name'], infomation['core_com6'].format(self.cores_setting[core_id]['heat']),\
                infomation['core_com14'].format(infomation['{}_name'.format(self.cores_setting[core_id]['coolant'])]), rod_inf,\
                infomation['{}_core'.format(self.cores_setting[core_id]['coolant'])])
            message = self.cores_setting[core_id]['core_inf'][k]
            exec('self.core{0}_{1}_cell{2}.unbind(\'<Enter>\')'.format(i,j,k))
            exec('self.core{0}_{1}_cell{2}.bind(\'<Enter>\',self.functionAdaptor(self.Balloon_show, msg=message))'.format(i,j,k))

    def get_rod_inf(self, rod):
        if rod == None:
            rod_inf = infomation['core_com0'].format(infomation['empty'])
        else:
            rod_inf = '{}'.format(infomation['core_com0'].format(infomation['{}_name'.format(rod['id'])]))
            if all_rods[rod['id']]['type'] == 'fuel_rod':
                if not rod['depleted']:
                    rod_inf += '\n{}'.format(infomation['core_com2'].format(rod['life']/60))
                    if rod['active']:
                        rod_inf += '\n{}'.format(infomation['core_com1'].format(rod['neutron']))
                        rod_inf += '\n{}'.format(infomation['core_com11'].format(rod['life_multi']))
                        rod_inf += '\n{}'.format(infomation['core_com8'].format(infomation['precent'].format(rod['utilization_N']*100)))
                        if rod['overloaded']:
                            rod_inf += '{}'.format(infomation['core_com10'])
                        if rod['moderated']:
                            rod_inf += '\n{}'.format(infomation['core_com5'])
                    else: rod_inf += '\n{}'.format(infomation['core_com13'])
                else:
                    rod_inf += '\n{}'.format(infomation['core_com9'])
                    #...
            elif all_rods[rod['id']]['type'] == 'absorb_rod':
                if rod['active']: rod_inf += '\n{}'.format(infomation['core_com1'].format(rod['neutron']))
                else: rod_inf += '\n{}'.format(infomation['core_com13'])
            elif all_rods[rod['id']]['type'] == 'breed_rod':
                rod_inf += '\n{}'.format(infomation['core_com3'].format(rod['needed']))
                if rod['active']: 
                    rod_inf += '\n{}'.format(infomation['core_com1'].format(rod['neutron']))
                    rod_inf += '\n{}'.format(infomation['core_com12'].format(rod['truning_speed']))
                else: rod_inf += '\n{}'.format(infomation['core_com13'])
        return rod_inf

    #反应堆交互
    def click_core(self, event, posijk):
        if not self.is_start:
            i,j,k = posijk
            if event.num == 1:
                tool_id = self.mouse_setting['m1']
            elif event.num == 3:
                tool_id = self.mouse_setting['m2']
            core_id = 'core{}_{}'.format(i,j)

            if tool_id != None:
                if tool_id == 'core1x1':
                    if self.cores_setting[core_id]['base'] == None:
                        self.cores_setting[core_id]['base'] = 'core1x1'
                        self.cores_setting[core_id]['rod'] = None
                        self.cores_setting[core_id]['core_inf'] = None
                elif tool_id == 'core2x2':
                    if self.cores_setting[core_id]['base'] == None:
                        self.cores_setting[core_id]['base'] = 'core2x2'
                        self.cores_setting[core_id]['rod'] = [None, None, None, None]
                        self.cores_setting[core_id]['core_inf'] = [None, None, None, None]
                elif tool_id == 'wrench':
                    if self.cores_setting[core_id]['base'] != None:
                        self.reset_core_setting(core_id)
                        self.draw_core_specific(posijk)
                        self.Balloon_destroy()
                        self.change_core_dis((i,j))
                elif tool_id == 'pliers':
                    if self.cores_setting[core_id]['base'] != None:
                        self.set_core_rod(posijk, None)
                        self.draw_core_specific(posijk, False if k==-1 else True)
                        if self.cores_setting[core_id]['base'] == 'core1x1': self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'])
                        elif self.cores_setting[core_id]['base'] == 'core2x2': self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'][k])
                        self.change_core_dis((i,j))
                elif tool_id == 'soft_hammer':
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        if self.cores_setting[core_id]['rod'] != None:
                            self.reset_core_rod(posijk)
                            self.cores_setting[core_id]['rod']['active'] = not self.cores_setting[core_id]['rod']['active']
                            self.cores_setting[core_id]['rod']['life_multi'] = 1 if self.cores_setting[core_id]['rod']['active'] else 0
                            self.draw_core_specific(posijk)
                            self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'])
                            self.change_core_dis((i,j))
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        if self.cores_setting[core_id]['rod'][k] != None:
                            self.reset_core_rod(posijk)
                            self.cores_setting[core_id]['rod'][k]['active'] = not self.cores_setting[core_id]['rod'][k]['active']
                            self.cores_setting[core_id]['rod'][k]['life_multi'] = 1 if self.cores_setting[core_id]['rod'][k]['active'] else 0
                            self.draw_core_specific(posijk, True)
                            self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'][k])
                            self.change_core_dis((i,j))
                elif 'rod' in tool_id:
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        if self.cores_setting[core_id]['rod'] == None:
                            self.set_core_rod(posijk, rod_id=tool_id)
                            self.draw_core_specific(posijk)
                            self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'])
                            self.change_core_dis((i,j))
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        if self.cores_setting[core_id]['rod'][k] == None:
                            self.set_core_rod(posijk, rod_id=tool_id)
                            self.draw_core_specific(posijk, True)
                            self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'][k])
                            self.change_core_dis((i,j))
            #冷却剂部分
            coolant_id = self.mouse_setting['coolant']
            if tool_id in ['core1x1','core2x2']:
                if self.cores_setting[core_id]['base'] == 'core1x1':
                    self.cores_setting[core_id]['coolant'] = coolant_id
                    self.draw_core_specific(posijk)
                    self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'])
                    self.change_core_dis((i,j))
                elif self.cores_setting[core_id]['base'] == 'core2x2':
                    self.cores_setting[core_id]['coolant'] = coolant_id
                    self.draw_core_specific(posijk)
                    self.Balloon_show(event,msg=self.cores_setting[core_id]['core_inf'][k])
                    self.change_core_dis((i,j))

    def draw_core_specific(self, posijk, quarter=False):
        i,j,k = posijk
        core_size = 600//self.core_num
        core_id = 'core{}_{}'.format(i,j)
        basetype = self.cores_setting[core_id]['base']
        if not quarter: # 改变行为是否是四分之一单位的
            if basetype == None:
                if k == -1: # 改变的对象是否是四分之一的
                    exec('{0}_cell0Tex = bgimg.resize(({1},{1}), PIL.Image.NEAREST)'.format(core_id, core_size-4))
                    exec('{0}_cell0TexTk = PIL.ImageTk.PhotoImage({0}_cell0Tex)'.format(core_id))
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_image, image={0}_cell0TexTk)'.format(core_id))
                    exec('self.{0}_cell0TexTk = {0}_cell0TexTk'.format(core_id)) # keep img not be deleted
                    self.set_core_inf((i,j,-1))
                else:
                    for k in range(4):
                        exec('self.{0}_cell{1}.destroy()'.format(core_id, k))
                    self.form_core_cell((i,j), False)
            elif basetype == 'core1x1':
                if k == -1: # 改变的对象是否是四分之一的
                    exec('{0}_cell0Tex = core1x1topimg.resize(({1},{1}), PIL.Image.NEAREST)'.format(core_id, core_size-4))
                    rod = self.cores_setting[core_id]['rod']
                    if rod != None:
                        if rod['active']: exec('rodTex = {0}topimg.resize(({1},{1}), PIL.Image.NEAREST)'.format(rod['id'], core_size-4))
                        else: exec('rodTex = {0}top_closeimg.resize(({1},{1}), PIL.Image.NEAREST)'.format(rod['id'], core_size-4))
                        exec('{0}_cell0Tex = PIL.Image.alpha_composite({0}_cell0Tex, rodTex)'.format(core_id))
                    exec('{0}_cell0TexTk = PIL.ImageTk.PhotoImage({0}_cell0Tex)'.format(core_id))
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_image, image={0}_cell0TexTk)'.format(core_id))
                    exec('self.{0}_cell0TexTk = {0}_cell0TexTk'.format(core_id)) # keep img not be deleted
                    self.set_core_inf((i,j,-1))
                else:
                    for k in range(4):
                        exec('self.{0}_cell{1}.destroy()'.format(core_id, k))
                    self.form_core_cell((i,j), False)
            elif basetype == 'core2x2':
                if k == -1: # 改变的对象是否是四分之一的
                    exec('self.{0}_cell0.destroy()'.format(core_id))
                    self.form_core_cell((i,j), True)
                else:
                    for k in range(4):
                        exec('{0}_cell{1}Tex = core2x2top_partimg.resize(({2},{2}), PIL.Image.NEAREST)'.format(core_id, k, core_size//2-2))
                        rod = self.cores_setting[core_id]['rod'][k]
                        if rod != None:
                            if rod['active']: exec('rodTex_part = {0}topimg.crop((4,4,12,12))'.format(rod['id']))
                            else: exec('rodTex_part = {0}top_closeimg.crop((4,4,12,12))'.format(rod['id']))
                            exec('rodTex_part = rodTex_part.resize(({0},{0}), PIL.Image.NEAREST)'.format(core_size//2-2))
                            exec('{0}_cell{1}Tex = PIL.Image.alpha_composite({0}_cell{1}Tex, rodTex_part)'.format(core_id, k))
                        exec('{0}_cell{1}TexTk = PIL.ImageTk.PhotoImage({0}_cell{1}Tex)'.format(core_id, k))
                        exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_image, image={0}_cell{1}TexTk)'.format(core_id, k))
                        exec('self.{0}_cell{1}TexTk = {0}_cell{1}TexTk'.format(core_id, k)) # keep img not be deleted
                        self.set_core_inf((i,j,k))
        else:
            if basetype == 'core2x2' and k != -1:
                exec('{0}_cell{1}Tex = core2x2top_partimg.resize(({2},{2}), PIL.Image.NEAREST)'.format(core_id, k, core_size//2-2))
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None:
                    if rod['active']: exec('rodTex_part = {0}topimg.crop((4,4,12,12))'.format(rod['id']))
                    else: exec('rodTex_part = {0}top_closeimg.crop((4,4,12,12))'.format(rod['id']))
                    exec('rodTex_part = rodTex_part.resize(({0},{0}), PIL.Image.NEAREST)'.format(core_size//2-2))
                    exec('{0}_cell{1}Tex = PIL.Image.alpha_composite({0}_cell{1}Tex, rodTex_part)'.format(core_id, k))
                exec('{0}_cell{1}TexTk = PIL.ImageTk.PhotoImage({0}_cell{1}Tex)'.format(core_id, k))
                exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_image, image={0}_cell{1}TexTk)'.format(core_id, k))
                exec('self.{0}_cell{1}TexTk = {0}_cell{1}TexTk'.format(core_id, k)) # keep img not be deleted
                self.set_core_inf(posijk)

    #信息
    def form_core_dis(self, posijk, core_size):
        ##输入必须有效！
        i,j,k=posijk
        core_id = 'core{}_{}'.format(i,j)
        if k != -1:
            ##names
            exec('self.{0}_cell{1}_nameRtext=self.{0}_cell{1}.create_text({2}+1,{2},text=\'\', anchor=NW, font=font_namesR)'.format(core_id, k, (core_size//2-2)//4))
            if k == 0:
                exec('self.{0}_cell{1}_nameCtext=self.{0}_cell{1}.create_text(0,0,text=\'\', anchor=NW, font=font_namesC)'.format(core_id, k))
            ##heat
            if k == 3:
                exec('self.{0}_cell{1}_heattext=self.{0}_cell{1}.create_text({2},{2},text=\'\', anchor=SE, font=font_heat)'.format(core_id, k, core_size//2-2))
            ##neutron
            exec('self.{0}_cell{1}_neutrontext=self.{0}_cell{1}.create_text({2},{2}+1,text=\'\', anchor=SE, font=font_namesR,fill=\'#350071\')'.format(core_id, k, (core_size//2-2)*3//4))
            ##fluid
            if k == 1:
                exec('self.{0}_cell{1}_fluidtext=self.{0}_cell{1}.create_text({2},0,text=\'\', anchor=NE, font=font_heat)'.format(core_id, k, core_size//2-2))
            ##moderate
            exec('self.{0}_cell{1}_modtext=self.{0}_cell{1}.create_text({2},{2},text=\'\', anchor=CENTER, font=font_namesC,fill=\'#2300a5\')'.format(core_id, k, (core_size//2-2)//2))
            ##utilization
            exec('self.{0}_cell{1}_utitext=self.{0}_cell{1}.create_text({2},{3},text=\'\', anchor=SE, font=font_namesR)'.format(core_id, k, (core_size//2-2)*3//4, (core_size//2-2)//4))
            ##progress
            exec('self.{0}_cell{1}_progtext=self.{0}_cell{1}.create_text({3},{2},text=\'\', anchor=NW, font=font_namesR)'.format(core_id, k, (core_size//2-2)*3//4, (core_size//2-2)//4))
        elif k == -1:
            ##names
            exec('self.{0}_cell0_nameRtext=self.{0}_cell0.create_text({1}+2,{1}+1,text=\'\', anchor=NW, font=font_namesR)'.format(core_id, (core_size-4)*6//16))
            exec('self.{0}_cell0_nameCtext=self.{0}_cell0.create_text(0,0,text=\'\', anchor=NW, font=font_namesC)'.format(core_id))
            ##heat
            exec('self.{0}_cell0_heattext=self.{0}_cell0.create_text({1},{1},text=\'\', anchor=SE, font=font_heat)'.format(core_id, core_size-4))
            ##neutron
            exec('self.{0}_cell0_neutrontext=self.{0}_cell0.create_text({1}-1,{1},text=\'\', anchor=SE, font=font_namesR,fill=\'#350071\')'.format(core_id, (core_size-4)*10//16))
            ##fluid
            exec('self.{0}_cell0_fluidtext=self.{0}_cell0.create_text({1},0,text=\'\', anchor=NE, font=font_heat)'.format(core_id, core_size-4))
            ##moderate
            exec('self.{0}_cell0_modtext=self.{0}_cell0.create_text({1},{1},text=\'\', anchor=CENTER, font=font_namesC,fill=\'#2300a5\')'.format(core_id, (core_size-4)//2))
            ##utilization
            exec('self.{0}_cell0_utitext=self.{0}_cell0.create_text({1},{2},text=\'\', anchor=SE, font=font_namesR)'.format(core_id, (core_size-4)*10//16, (core_size-4)*6//16))
            ##progress
            exec('self.{0}_cell0_progtext=self.{0}_cell0.create_text({2},{1},text=\'\', anchor=NW, font=font_namesR)'.format(core_id, (core_size-4)*10//16, (core_size-4)*6//16))

    def change_core_dis(self, posij):
        i,j = posij
        if i>=0 and j>=0 and i<self.core_num and j<self.core_num:
            core_id = 'core{}_{}'.format(i,j)
            if self.cores_setting[core_id]['base'] == None:
                ##name
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_nameRtext, text=\'\')'.format(core_id))
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_nameCtext, text=\'\')'.format(core_id))
                ##heat
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_heattext, text=\'\')'.format(core_id))
                ##neutron
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_neutrontext, text=\'\')'.format(core_id))
                ##fluid
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_fluidtext, text=\'\')'.format(core_id))
                ##moderate
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_modtext, text=\'\')'.format(core_id))
                ##utilization
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_utitext, text=\'\')'.format(core_id))
                ##progress
                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_progtext, text=\'\')'.format(core_id))
            elif self.cores_setting[core_id]['base'] == 'core1x1':
                rod = self.cores_setting[core_id]['rod']
                ##name
                if self.display_setting['names']:
                    if rod != None:
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_nameRtext, text=all_rods[rod[\'id\']][\'name\'],fill=all_rods[rod[\'id\']][\'name_col\'])'.format(core_id))
                    else:
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_nameRtext, text=\'\')'.format(core_id))
                    coolant = all_coolant[self.cores_setting[core_id]['coolant']]
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_nameCtext, text=coolant[\'name\'],fill=coolant[\'name_col\'])'.format(core_id))
                else:
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_nameRtext, text=\'\')'.format(core_id))
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_nameCtext, text=\'\')'.format(core_id))
                ##heat
                if self.display_setting['heat']:
                    heat = self.cores_setting[core_id]['heat']
                    heat_t = '{:.0f} HU/t'.format(heat)
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_heattext, text=heat_t,fill=self.heat2col(heat))'.format(core_id))
                else:
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_heattext, text=\'\')'.format(core_id))
                ##neutron
                if self.display_setting['neutron']:
                    if rod != None:
                        try: neutron = rod['neutron']
                        except: neutron = 0
                        neutron_t = '{} N'.format(neutron)
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_neutrontext, text=neutron_t)'.format(core_id))
                    else:
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_neutrontext, text=\'\')'.format(core_id))
                else:
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_neutrontext, text=\'\')'.format(core_id))
                ##fluid
                if self.display_setting['fluid']:
                    fluid = self.cores_setting[core_id]['fluid']
                    if self.cores_setting[core_id]['coolant'] == 'molten_thorium_salt':
                        fluid_t = '{:.1f} L/Sec'.format(fluid*20)
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_fluidtext, text=fluid_t,fill=self.fluid2col(fluid*20))'.format(core_id))
                    else:
                        fluid_t = '{:.1f} L/t'.format(fluid)
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_fluidtext, text=fluid_t,fill=self.fluid2col(fluid))'.format(core_id))
                else:
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_fluidtext, text=\'\')'.format(core_id))
                ##moderate
                if self.display_setting['moderate']:
                    if rod != None and all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']) and rod['moderated']:
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_modtext, text=\'M\')'.format(core_id))
                    else:
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_modtext, text=\'\')'.format(core_id))
                else:
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_modtext, text=\'\')'.format(core_id))
                ##utilization
                if self.display_setting['utilization']:
                    if rod != None and all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                        utilization = rod['utilization_N']
                        utilization_t = '{:.1f}%'.format(utilization*100)
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_utitext, text=utilization_t,fill=self.uti2col(utilization))'.format(core_id))
                    else:
                        exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_utitext, text=\'\')'.format(core_id))
                else:
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_utitext, text=\'\')'.format(core_id))
                ##progress
                if self.display_setting['progress']:
                    progress_t = ''
                    progress_c = '#ffffff'
                    if rod != None:
                        if all_rods[rod['id']]['type'] == 'fuel_rod':
                            if not rod['depleted']:
                                progress = rod['life']/all_rods[rod['id']]['detail']['life']
                                progress_t = '{:.1f}%'.format(progress*100)
                                progress_c = '#ffffff'
                                exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_progtext, text=progress_t,fill=progress_c)'.format(core_id))
                            else:
                                progress_t = 'Dead'
                                progress_c = '#ff3c3c'
                        elif all_rods[rod['id']]['type'] == 'breed_rod':
                            progress = rod['needed']/all_rods[rod['id']]['detail']['needed']
                            progress_t = '{:.1f}%'.format(progress*100)
                            progress_c = '#ffffff'
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_progtext, text=progress_t,fill=progress_c)'.format(core_id))
                else:
                    exec('self.{0}_cell0.itemconfigure(self.{0}_cell0_progtext, text=\'\')'.format(core_id))
            elif self.cores_setting[core_id]['base'] == 'core2x2':
                for k in range(4):
                    rod = self.cores_setting[core_id]['rod'][k]
                    ##name
                    if k == 0:
                        if self.display_setting['names']:
                            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_nameCtext, text=coolant[\'name\'],fill=coolant[\'name_col\'])'.format(core_id,k))
                        else: 
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_nameCtext, text=\'\')'.format(core_id,k))
                    if self.display_setting['names']:
                        if rod != None:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_nameRtext, text=all_rods[rod[\'id\']][\'name\'],fill=all_rods[rod[\'id\']][\'name_col\'])'.format(core_id,k))
                        else:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_nameRtext, text=\'\')'.format(core_id,k))
                    else:
                        exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_nameRtext, text=\'\')'.format(core_id,k))
                    ##heat
                    if k == 3:
                        if self.display_setting['heat']:
                            heat = self.cores_setting[core_id]['heat']
                            heat_t = '{:.0f} HU/t'.format(heat)
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_heattext, text=heat_t,fill=self.heat2col(heat))'.format(core_id,k))
                        else:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_heattext, text=\'\')'.format(core_id,k))
                    ##neutron
                    if self.display_setting['neutron']:
                        if rod != None:
                            try: neutron = rod['neutron']
                            except: neutron = 0
                            neutron_t = '{} N'.format(neutron)
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_neutrontext, text=neutron_t)'.format(core_id,k))
                        else:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_neutrontext, text=\'\')'.format(core_id,k))
                    else:
                        exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_neutrontext, text=\'\')'.format(core_id,k))
                    ##fluid
                    if k == 1:
                        if self.display_setting['fluid']:
                            fluid = self.cores_setting[core_id]['fluid']
                            if self.cores_setting[core_id]['coolant'] == 'molten_thorium_salt':
                                fluid_t = '{:.1f} L/Sec'.format(fluid*20)
                                exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_fluidtext, text=fluid_t,fill=self.fluid2col(fluid*20))'.format(core_id, k))
                            else:
                                fluid_t = '{:.1f} L/t'.format(fluid)
                                exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_fluidtext, text=fluid_t,fill=self.fluid2col(fluid))'.format(core_id, k))
                        else:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_fluidtext, text=\'\')'.format(core_id,k))
                    ##moderate
                    if self.display_setting['moderate']:
                        if rod != None and all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']) and rod['moderated']:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_modtext, text=\'M\')'.format(core_id,k))
                        else:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_modtext, text=\'\')'.format(core_id,k))
                    else:
                        exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_modtext, text=\'\')'.format(core_id,k))
                    ##utilization
                    if self.display_setting['utilization']:
                        if rod != None and all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                            utilization = rod['utilization_N']
                            utilization_t = '{:.1f}%'.format(utilization*100)
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_utitext, text=utilization_t,fill=self.uti2col(utilization))'.format(core_id,k))
                        else:
                            exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_utitext, text=\'\')'.format(core_id,k))
                    else:
                        exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_utitext, text=\'\')'.format(core_id,k))
                    ##progress
                    if self.display_setting['progress']:
                        progress_t = ''
                        progress_c = '#ffffff'
                        if rod != None:
                            if all_rods[rod['id']]['type'] == 'fuel_rod':
                                if not rod['depleted']:
                                    progress = rod['life']/all_rods[rod['id']]['detail']['life']
                                    progress_t = '{:.1f}%'.format(progress*100)
                                    progress_c = '#ffffff'
                                    exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_progtext, text=progress_t,fill=progress_c)'.format(core_id,k))
                                else:
                                    progress_t = 'Dead'
                                    progress_c = '#ff3c3c'
                            elif all_rods[rod['id']]['type'] == 'breed_rod':
                                progress = rod['needed']/all_rods[rod['id']]['detail']['needed']
                                progress_t = '{:.1f}%'.format(progress*100)
                                progress_c = '#ffffff'
                        exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_progtext, text=progress_t,fill=progress_c)'.format(core_id,k))
                    else:
                        exec('self.{0}_cell{1}.itemconfigure(self.{0}_cell{1}_progtext, text=\'\')'.format(core_id,k))



    def draw_all(self, reform=True, draw=True, dis=True):
        if reform:
            for i in range(self.core_num):
                for j in range(self.core_num):
                    exec('self.core{}_{}.destroy()'.format(i,j))
            self.core_num = self.cores_setting['core_num']
            self.form_core()
        elif draw:
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    if self.cores_setting[core_id]['base'] == 'core2x2':
                        self.draw_core_specific((i,j,0))
                    else: self.draw_core_specific((i,j,-1))
        if dis:
            for i in range(self.core_num):
                for j in range(self.core_num):
                    self.change_core_dis((i,j))

###############################################

    def spread_moderated(self, posij, direction):
        i,j = posij
        out = False
        if i>=0 and j>=0 and i<self.core_num and j<self.core_num:
            core_id = 'core{}_{}'.format(i,j)
            if self.cores_setting[core_id]['base'] == 'core1x1':
                rod = self.cores_setting[core_id]['rod']
                if rod != None and rod['active']:
                    rod_type = all_rods[rod['id']]['type']
                    if rod_type=='fuel_rod' and (not rod['depleted']):
                        if rod['moderated']:
                            out = True
                    elif rod_type=='moderate_rod':
                        out = True
            elif self.cores_setting[core_id]['base'] == 'core2x2':
                for k in range(4):
                    if k in direction:
                        rod = self.cores_setting[core_id]['rod'][k]
                        if rod != None and rod['active']:
                            rod_type = all_rods[rod['id']]['type']
                            if rod_type=='fuel_rod' and (not rod['depleted']):
                                if rod['moderated']:
                                    out = True
                            elif rod_type=='moderate_rod':
                                out = True
        return out

    def check_moderated(self,posij):
        i,j = posij
        core_id = 'core{}_{}'.format(i,j)
        if self.cores_setting[core_id]['base'] == 'core1x1':
            has_moderated = None
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            rod = self.cores_setting[core_id]['rod']
            if rod != None and rod['active']:
                if all_rods[rod['id']]['type']=='fuel_rod' and (not rod['depleted']):
                    if coolant['moderate']:
                        has_moderated = True
                    else:
                        has_moderated = False
                        has_moderated |= self.spread_moderated((i-1,j), (2,3))
                        has_moderated |= self.spread_moderated((i+1,j), (0,1))
                        has_moderated |= self.spread_moderated((i,j-1), (1,3))
                        has_moderated |= self.spread_moderated((i,j+1), (0,2))
            return has_moderated, 'core1x1'
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            has_moderated = [None, None, None, None]
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            for k in range(4):
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    if all_rods[rod['id']]['type']=='fuel_rod' and (not rod['depleted']):
                        if coolant['moderate']:
                            has_moderated[k] = True
                        else:
                            has_moderated[k] = False
                            if k == 0:
                                has_moderated[k] |= self.spread_moderated((i-1,j), (2,))
                                has_moderated[k] |= self.spread_moderated((i,j),   (2,))
                                has_moderated[k] |= self.spread_moderated((i,j-1), (1,))
                                has_moderated[k] |= self.spread_moderated((i,j),   (1,))
                            if k == 1:
                                has_moderated[k] |= self.spread_moderated((i-1,j), (3,))
                                has_moderated[k] |= self.spread_moderated((i,j),   (3,))
                                has_moderated[k] |= self.spread_moderated((i,j),   (0,))
                                has_moderated[k] |= self.spread_moderated((i,j+1), (0,))
                            if k == 2:
                                has_moderated[k] |= self.spread_moderated((i,j),   (0,))
                                has_moderated[k] |= self.spread_moderated((i+1,j), (0,))
                                has_moderated[k] |= self.spread_moderated((i,j-1), (3,))
                                has_moderated[k] |= self.spread_moderated((i,j),   (3,))
                            if k == 3:
                                has_moderated[k] |= self.spread_moderated((i,j),   (1,))
                                has_moderated[k] |= self.spread_moderated((i+1,j), (1,))
                                has_moderated[k] |= self.spread_moderated((i,j),   (2,))
                                has_moderated[k] |= self.spread_moderated((i,j+1), (2,))
            return has_moderated, 'core2x2'
        elif self.cores_setting[core_id]['base'] == None:
            return None, None

    def get_active_num(self, posij, direction):
        i,j = posij
        active_num = 0
        if i>=0 and j>=0 and i<self.core_num and j<self.core_num:
            core_id = 'core{}_{}'.format(i,j)
            if self.cores_setting[core_id]['base'] == 'core1x1':
                rod = self.cores_setting[core_id]['rod']
                if rod != None and rod['active']:
                    if all_rods[rod['id']]['type']=='fuel_rod' and (not rod['depleted']):
                       active_num+=len(direction) #1x1的燃料棒对于1x1的减速棒为2个
            elif self.cores_setting[core_id]['base'] == 'core2x2':
                for k in range(4):
                    if k in direction:
                        rod = self.cores_setting[core_id]['rod'][k]
                        if rod != None and rod['active']:
                            if all_rods[rod['id']]['type']=='fuel_rod' and (not rod['depleted']):
                               active_num+=1
        return active_num

    def cal_multi_num(self, posij):
        i,j = posij
        core_id = 'core{}_{}'.format(i,j)
        if self.cores_setting[core_id]['base'] == 'core1x1':
            multi = None
            rod = self.cores_setting[core_id]['rod']
            if rod != None and rod['active']:
                if all_rods[rod['id']]['type']=='moderate_rod':
                    #统计周围激活数
                    multi = 0
                    multi += self.get_active_num((i-1,j), (2,3))
                    multi += self.get_active_num((i+1,j), (0,1))
                    multi += self.get_active_num((i,j-1), (1,3))
                    multi += self.get_active_num((i,j+1), (0,2))
            return multi, 'core1x1'
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            multi = [None, None, None, None]
            for k in range(4):
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    if all_rods[rod['id']]['type']=='moderate_rod':
                        #统计周围激活数
                        multi[k] = 0
                        if k == 0:
                            multi[k] += self.get_active_num((i-1,j), (2,))
                            multi[k] += self.get_active_num((i,j),   (2,))
                            multi[k] += self.get_active_num((i,j-1), (1,))
                            multi[k] += self.get_active_num((i,j),   (1,))
                        if k == 1:
                            multi[k] += self.get_active_num((i-1,j), (3,))
                            multi[k] += self.get_active_num((i,j),   (3,))
                            multi[k] += self.get_active_num((i,j),   (0,))
                            multi[k] += self.get_active_num((i,j+1), (0,))
                        if k == 2:
                            multi[k] += self.get_active_num((i,j),   (0,))
                            multi[k] += self.get_active_num((i+1,j), (0,))
                            multi[k] += self.get_active_num((i,j-1), (3,))
                            multi[k] += self.get_active_num((i,j),   (3,))
                        if k == 3:
                            multi[k] += self.get_active_num((i,j),   (1,))
                            multi[k] += self.get_active_num((i+1,j), (1,))
                            multi[k] += self.get_active_num((i,j),   (2,))
                            multi[k] += self.get_active_num((i,j+1), (2,))
            return multi, 'core2x2'
        elif self.cores_setting[core_id]['base'] == None:
            return None, None

    def cal_emissiom_num(self, posij, is_moderated=False):
        i,j = posij
        core_id = 'core{}_{}'.format(i,j)
        if self.cores_setting[core_id]['base'] == 'core1x1':
            En,s = None,None
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            rod = self.cores_setting[core_id]['rod']
            if rod != None and rod['active']:
                rod_type = all_rods[rod['id']]['type']
                if rod_type == 'fuel_rod' and (not rod['depleted']):
                    if not (rod['moderated'] ^ is_moderated):
                        e = round(all_rods[rod['id']]['detail']['emission'] * coolant['emission'])
                        s = round(all_rods[rod['id']]['detail']['self'] * coolant['self'])
                        exec('self.f = round({})'.format(coolant['factor'].format(all_rods[rod['id']]['detail']['factor'])))
                        f = 1/self.f
                        n = rod['neutron']
                        En = ceil((e + ((n-s)*f))/2)
            return En, 'core1x1', s
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            En = [None, None, None, None]
            s = [None, None, None, None]
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            for k in range(4):
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    rod_type = all_rods[rod['id']]['type']
                    if rod_type == 'fuel_rod' and (not rod['depleted']):
                        if not (rod['moderated'] ^ is_moderated):
                            e = round(all_rods[rod['id']]['detail']['emission'] * coolant['emission'])
                            s[k] = round(all_rods[rod['id']]['detail']['self'] * coolant['self'])
                            exec('self.f = round({})'.format(coolant['factor'].format(all_rods[rod['id']]['detail']['factor'])))
                            f = 1/self.f
                            n = rod['neutron']
                            En[k] = ceil(e + ((n-s[k])*f))
            return En, 'core2x2', s
        elif self.cores_setting[core_id]['base'] == None:
            return None, None, None

    def get_neutron(self, posijk, oposijk, neutron_num, is_moderated=False):
        i,j,k = posijk
        oi,oj,ok = oposijk
        ocore_id = 'core{}_{}'.format(oi,oj)
        if i>=0 and j>=0 and i<self.core_num and j<self.core_num:
            core_id = 'core{}_{}'.format(i,j)
            get_neutron_str = 'get_neutron'
            if is_moderated: get_neutron_str += '_moderated'
            if self.cores_setting[core_id]['base'] == 'core1x1':
                rod = self.cores_setting[core_id]['rod']
                if rod != None and rod['active']:
                    rod_type = all_rods[rod['id']]['type']
                    if (rod_type == 'fuel_rod' and (not rod['depleted'])) or rod_type == 'absorb_rod' or rod_type == 'breed_rod':
                        self.cores_setting[core_id]['rod'][get_neutron_str] += neutron_num
                    elif rod_type == 'reflect_rod':
                        if ok == -1: self.cores_setting[ocore_id]['rod'][get_neutron_str] += neutron_num
                        else:        self.cores_setting[ocore_id]['rod'][ok][get_neutron_str] += neutron_num
                    elif rod_type == 'moderate_rod' and is_moderated:
                        if ok == -1: self.cores_setting[ocore_id]['rod']['get_neutron_moderated'] += neutron_num*self.cores_setting[core_id]['rod']['multi']
                        else:        self.cores_setting[ocore_id]['rod'][ok]['get_neutron_moderated'] += neutron_num*self.cores_setting[core_id]['rod']['multi']
            elif self.cores_setting[core_id]['base'] == 'core2x2':
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    rod_type = all_rods[rod['id']]['type']
                    if (rod_type == 'fuel_rod' and (not rod['depleted'])) or rod_type == 'absorb_rod' or rod_type == 'breed_rod':
                        self.cores_setting[core_id]['rod'][k][get_neutron_str] += neutron_num
                    elif rod_type == 'reflect_rod':
                        if ok == -1: self.cores_setting[ocore_id]['rod'][get_neutron_str] += neutron_num
                        else:        self.cores_setting[ocore_id]['rod'][ok][get_neutron_str] += neutron_num
                    elif rod_type == 'moderate_rod' and is_moderated:
                        if ok == -1: self.cores_setting[ocore_id]['rod']['get_neutron_moderated'] += neutron_num*self.cores_setting[core_id]['rod'][k]['multi']
                        else:        self.cores_setting[ocore_id]['rod'][ok]['get_neutron_moderated'] += neutron_num*self.cores_setting[core_id]['rod'][k]['multi']

    # 切换
    def switch_neutron(self, posij):
        i,j = posij
        core_id = 'core{}_{}'.format(i,j)
        get_neutron_str = 'get_neutron'
        if self.cores_setting[core_id]['base'] == 'core1x1':
            rod = self.cores_setting[core_id]['rod']
            if rod != None and rod['active']:
                rod_type = all_rods[rod['id']]['type']
                if rod_type == 'fuel_rod' and (not rod['depleted']):
                    get_neutron_num = self.cores_setting[core_id]['rod']['get_neutron']
                    get_neutron_moderated_num = self.cores_setting[core_id]['rod']['get_neutron_moderated']
                    self.cores_setting[core_id]['rod']['neutron'] = get_neutron_num + get_neutron_moderated_num
                    self.cores_setting[core_id]['rod']['get_neutron'] = 0
                    self.cores_setting[core_id]['rod']['get_neutron_moderated'] = 0
                elif rod_type == 'absorb_rod':
                    get_neutron_num = self.cores_setting[core_id]['rod']['get_neutron']
                    get_neutron_moderated_num = self.cores_setting[core_id]['rod']['get_neutron_moderated']
                    self.cores_setting[core_id]['rod']['neutron'] = get_neutron_num + get_neutron_moderated_num
                    self.cores_setting[core_id]['rod']['get_neutron'] = 0
                    self.cores_setting[core_id]['rod']['get_neutron_moderated'] = 0
                elif rod_type == 'breed_rod':
                    get_neutron_num = self.cores_setting[core_id]['rod']['get_neutron']
                    self.cores_setting[core_id]['rod']['get_neutron'] = 0
                    self.cores_setting[core_id]['rod']['get_neutron_moderated'] = 0
                    self.cores_setting[core_id]['rod']['neutron'] = get_neutron_num
                    self.cores_setting[core_id]['rod']['truning_speed'] = ceil(get_neutron_num * pow(1.5,(get_neutron_num/500)))
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            for k in range(4):
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    rod_type = all_rods[rod['id']]['type']
                    if rod_type == 'fuel_rod' and (not rod['depleted']):
                        get_neutron_num = self.cores_setting[core_id]['rod'][k]['get_neutron']
                        get_neutron_moderated_num = self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']
                        self.cores_setting[core_id]['rod'][k]['neutron'] = get_neutron_num + get_neutron_moderated_num
                        self.cores_setting[core_id]['rod'][k]['get_neutron'] = 0
                        self.cores_setting[core_id]['rod'][k]['get_neutron_moderated'] = 0
                    elif rod_type == 'absorb_rod':
                        get_neutron_num = self.cores_setting[core_id]['rod'][k]['get_neutron']
                        get_neutron_moderated_num = self.cores_setting[core_id]['rod'][k]['get_neutron_moderated']
                        self.cores_setting[core_id]['rod'][k]['neutron'] = get_neutron_num + get_neutron_moderated_num
                        self.cores_setting[core_id]['rod'][k]['get_neutron'] = 0
                        self.cores_setting[core_id]['rod'][k]['get_neutron_moderated'] = 0
                    elif rod_type == 'breed_rod':
                        get_neutron_num = self.cores_setting[core_id]['rod'][k]['get_neutron']
                        self.cores_setting[core_id]['rod'][k]['get_neutron'] = 0
                        self.cores_setting[core_id]['rod'][k]['get_neutron_moderated'] = 0
                        self.cores_setting[core_id]['rod'][k]['neutron'] = get_neutron_num
                        self.cores_setting[core_id]['rod'][k]['truning_speed'] = ceil(get_neutron_num * pow(1.5,(get_neutron_num/500)))

    #流体部分
    def cal_fluid(self, posij):
        i,j = posij
        core_id = 'core{}_{}'.format(i,j)
        fluid = 0
        if self.cores_setting[core_id]['base'] == 'core1x1':
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            rod = self.cores_setting[core_id]['rod']
            if rod != None and rod['active']:
                rod_type = all_rods[rod['id']]['type']
                if rod_type == 'fuel_rod' and (not rod['depleted']):
                    fluid = rod['neutron'] * coolant['fluid_eff'] / coolant['heat_capacity']
                elif rod_type == 'absorb_rod':
                    fluid = rod['neutron']*2 * coolant['fluid_eff'] / coolant['heat_capacity']
                elif rod_type == 'breed_rod':
                    fluid = rod['neutron']/2 * coolant['fluid_eff'] / coolant['heat_capacity']
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            for k in range(4):
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    rod_type = all_rods[rod['id']]['type']
                    if rod_type == 'fuel_rod' and (not rod['depleted']):
                        fluid += rod['neutron'] * coolant['fluid_eff'] / coolant['heat_capacity']
                    elif rod_type == 'absorb_rod':
                        fluid += rod['neutron']*2 * coolant['fluid_eff'] / coolant['heat_capacity']
                    elif rod_type == 'breed_rod':
                        fluid += rod['neutron']/2 * coolant['fluid_eff'] / coolant['heat_capacity']
        self.cores_setting[core_id]['fluid'] = fluid

    def cal_all_fluid(self):
        self.coolantkeys = list(all_coolant.keys())
        for coolant_id in self.coolantkeys:
            self.cores_setting['fluid'][coolant_id] = None
        for i in range(self.core_num):
            for j in range(self.core_num):
                core_id = 'core{}_{}'.format(i,j)
                coolant_id = self.cores_setting[core_id]['coolant']
                if coolant_id != None:
                    if self.cores_setting['fluid'][coolant_id] == None:
                        self.cores_setting['fluid'][coolant_id] = 0
                    self.cores_setting['fluid'][coolant_id] += self.cores_setting[core_id]['fluid']

    #产热部分
    def cal_heat(self, posij):
        i,j = posij
        core_id = 'core{}_{}'.format(i,j)
        heat = 0
        if self.cores_setting[core_id]['base'] == 'core1x1':
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            rod = self.cores_setting[core_id]['rod']
            if rod != None and rod['active']:
                rod_type = all_rods[rod['id']]['type']
                if rod_type == 'fuel_rod' and (not rod['depleted']):
                    heat = floor(rod['neutron'] * coolant['utilization'])
                elif rod_type == 'absorb_rod':
                    heat = floor(rod['neutron'] * 2 * coolant['utilization'])
                elif rod_type == 'breed_rod':
                    heat = floor((rod['neutron'] / 2) * coolant['utilization'])
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            coolant = all_coolant[self.cores_setting[core_id]['coolant']]
            for k in range(4):
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    rod_type = all_rods[rod['id']]['type']
                    if rod_type == 'fuel_rod' and (not rod['depleted']):
                        heat += floor(rod['neutron'] * coolant['utilization'])
                    elif rod_type == 'absorb_rod':
                        heat += floor(rod['neutron'] * 2 * coolant['utilization'])
                    elif rod_type == 'breed_rod':
                        heat += floor((rod['neutron'] / 2) * coolant['utilization'])
        self.cores_setting[core_id]['heat'] = heat

    def cal_all_heat(self):
        heat = 0
        for i in range(self.core_num):
            for j in range(self.core_num):
                core_id = 'core{}_{}'.format(i,j)
                heat += self.cores_setting[core_id]['heat']
        self.cores_setting['heat'] = heat

    def get_max_heat(self):
        mheat = 0
        for i in range(self.core_num):
            for j in range(self.core_num):
                core_id = 'core{}_{}'.format(i,j)
                if self.cores_setting[core_id]['base'] == 'core1x1':
                    rod = self.cores_setting[core_id]['rod']
                    if rod != None:
                        rod_type = all_rods[rod['id']]['type']
                        if rod_type == 'fuel_rod' and (not rod['depleted']):
                            mheat += all_rods[rod['id']]['detail']['maximum']
                elif self.cores_setting[core_id]['base'] == 'core2x2':
                    for k in range(4):
                        rod = self.cores_setting[core_id]['rod'][k]
                        if rod != None:
                            rod_type = all_rods[rod['id']]['type']
                            if rod_type == 'fuel_rod' and (not rod['depleted']):
                                mheat += all_rods[rod['id']]['detail']['maximum']
        return mheat

    def get_u100_heat(self):
        u100heat = 0
        for i in range(self.core_num):
            for j in range(self.core_num):
                core_id = 'core{}_{}'.format(i,j)
                if self.cores_setting[core_id]['base'] == 'core1x1':
                    rod = self.cores_setting[core_id]['rod']
                    if rod != None:
                        rod_type = all_rods[rod['id']]['type']
                        if rod_type == 'fuel_rod' and (not rod['depleted']):
                            u100heat += all_rods[rod['id']]['detail']['maximum']*rod['life_multi']
                elif self.cores_setting[core_id]['base'] == 'core2x2':
                    for k in range(4):
                        rod = self.cores_setting[core_id]['rod'][k]
                        if rod != None:
                            rod_type = all_rods[rod['id']]['type']
                            if rod_type == 'fuel_rod' and (not rod['depleted']):
                                u100heat += all_rods[rod['id']]['detail']['maximum']*rod['life_multi']
        return u100heat


    # 增殖部分
    def cal_breed(self, posij):
        i,j = posij
        core_id = 'core{}_{}'.format(i,j)
        if self.cores_setting[core_id]['base'] == 'core1x1':
            rod = self.cores_setting[core_id]['rod']
            if rod != None and rod['active']:
                if all_rods[rod['id']]['type'] == 'breed_rod':
                    self.cores_setting[core_id]['rod']['needed'] -= rod['truning_speed']
        elif self.cores_setting[core_id]['base'] == 'core2x2':
            for k in range(4):
                rod = self.cores_setting[core_id]['rod'][k]
                if rod != None and rod['active']:
                    if all_rods[rod['id']]['type'] == 'breed_rod':
                        self.cores_setting[core_id]['rod'][k]['needed'] -= rod['truning_speed']

    # 时间轴部分
    def clr_time_graph(self, tick=0):
        self.time_graph.coords(self.selline, (0,0,0,300))
        self.time_graph.itemconfigure(self.selline, fill='#000000')
        self.time_graph.itemconfigure(self.u100text, text='')
        for time_s in range(tick//20, (self.timegraph_setting['max_time']//20)+5):
            try: exec('self.time_graph.delete(self.timepoint{})'.format(time_s))
            except: pass

    # 统计信息部分
    def updeta_ttinf(self):
        self.data_ttheat['text'] = infomation['ttinf0'].format(self.cores_setting['ttheat'])
        self.data_pheat['text'] = infomation['ttinf1'].format(self.cores_setting['heat'])
        day = self.cores_setting['tttime']//86400
        hour = (self.cores_setting['tttime']%86400)//3600
        min_ = (self.cores_setting['tttime']%3600)//60
        sec = self.cores_setting['tttime']%60
        self.data_time['text'] = infomation['ttinf4'].format(day, hour, min_, sec)
        u100heat = self.get_u100_heat()
        if u100heat > 0:
            utilization = (self.cores_setting['heat']/u100heat)*100
            self.data_utilization['text'] = infomation['ttinf2'].format(infomation['precent'].format(utilization))
        else:
            self.data_utilization['text'] = infomation['ttinf2'].format('NA')
        self.coolantkeys = list(all_coolant.keys())
        i = 0
        for coolant_id in self.coolantkeys:
            fluid = self.cores_setting['fluid'][coolant_id]
            if fluid != None:
                if coolant_id == 'molten_thorium_salt':
                    fluid_t = '{}: {} ({})'.format(infomation[coolant_id+'_name'], infomation['core_com15'].format(fluid*20), infomation[coolant_id+'_out'])
                    exec('self.fluid_{0}[\'text\'] = fluid_t'.format(coolant_id))
                else:
                    fluid_t = '{}: {} ({})'.format(infomation[coolant_id+'_name'], infomation['core_com7'].format(fluid), infomation[coolant_id+'_out'])
                    exec('self.fluid_{0}[\'text\'] = fluid_t'.format(coolant_id))
                exec('self.fluid_{0}.grid(row={1}, column=0, padx=5, pady=1, sticky=NW)'.format(coolant_id,i))
                i += 1
            else:
                exec('self.fluid_{0}[\'text\'] = \'\''.format(coolant_id))
                exec('self.fluid_{0}.grid_forget()'.format(coolant_id))

    ##### 开始
    def start_sim(self, input_tick):
        #预测
        def predict():
            ##计算平均产热
            self.pheat = 0
            n = 0
            for t in range(self.timegraph_setting['max_time']//40, self.timegraph_setting['max_time']//20):
                exec('self.heat_t = self.cores_setting_{}[\'heat\']'.format(t))
                self.pheat = ((n*self.pheat) + self.heat_t)/(n+1)
                n += 1
            ##计算平均流量
            self.pfluid = {}
            for coolant_id in self.coolantkeys:
                self.pfluid[coolant_id] = None
                n = 0
                for t in range(self.timegraph_setting['max_time']//40, self.timegraph_setting['max_time']//20):
                    exec('self.fluid_t = self.cores_setting_{}[\'fluid\'][coolant_id]'.format(t))
                    if self.fluid_t != None:
                        if self.pfluid[coolant_id] == None: self.pfluid[coolant_id] = 0
                        self.pfluid[coolant_id] = ((n*self.pfluid[coolant_id]) + self.fluid_t)/(n+1)
                        n += 1
            ##计算预测时间
            final_pre_time = None
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        rod = self.cores_setting[core_id]['rod']
                        if rod != None and rod['active']:
                            if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                pre_time = (rod['life']/rod['life_multi'])*20
                                if final_pre_time == None or pre_time < final_pre_time:
                                    final_pre_time = pre_time
                            if all_rods[rod['id']]['type'] == 'breed_rod':
                                if rod['truning_speed'] > 0:
                                    pre_time = rod['needed']/rod['truning_speed']
                                    if final_pre_time == None or pre_time < final_pre_time:
                                        final_pre_time = pre_time
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        for k in range(4):
                            rod = self.cores_setting[core_id]['rod'][k]
                            if rod != None and rod['active']:
                                if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                    pre_time = (rod['life']/rod['life_multi'])*20
                                    if final_pre_time == None or pre_time < final_pre_time:
                                        final_pre_time = pre_time
                                if all_rods[rod['id']]['type'] == 'breed_rod':
                                    if rod['truning_speed'] > 0:
                                        pre_time = rod['needed']/rod['truning_speed']
                                        if final_pre_time == None or pre_time < final_pre_time:
                                            final_pre_time = pre_time
            if final_pre_time == None: final_pre_time = 0
            final_pre_time_s = final_pre_time//20
            ##推演预测
            ###产热和时间
            self.cores_setting['ttheat'] += final_pre_time_s*self.cores_setting['heat']*20
            self.cores_setting['tttime'] += final_pre_time_s
            ###损耗
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        rod = self.cores_setting[core_id]['rod']
                        if rod != None and rod['active']:
                            if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                self.cores_setting[core_id]['rod']['life'] -= final_pre_time_s*rod['life_multi']
                            if all_rods[rod['id']]['type'] == 'breed_rod':
                                self.cores_setting[core_id]['rod']['needed'] -= final_pre_time_s*rod['truning_speed']*20
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        for k in range(4):
                            rod = self.cores_setting[core_id]['rod'][k]
                            if rod != None and rod['active']:
                                if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                    self.cores_setting[core_id]['rod'][k]['life'] -= final_pre_time_s*rod['life_multi']
                                if all_rods[rod['id']]['type'] == 'breed_rod':
                                    self.cores_setting[core_id]['rod'][k]['needed'] -= final_pre_time_s*rod['truning_speed']*20
            ##计算利用率
            u100ttheat = 0
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        rod = self.cores_setting[core_id]['rod']
                        if rod != None and rod['active']:
                            if all_rods[rod['id']]['type'] == 'fuel_rod':
                                active_time = (all_rods[rod['id']]['detail']['life'] - rod['life'])*20
                                u100ttheat += active_time * all_rods[rod['id']]['detail']['maximum']
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        for k in range(4):
                            rod = self.cores_setting[core_id]['rod'][k]
                            if rod != None and rod['active']:
                                if all_rods[rod['id']]['type'] == 'fuel_rod':
                                    active_time = (all_rods[rod['id']]['detail']['life'] - rod['life'])*20
                                    u100ttheat += active_time * all_rods[rod['id']]['detail']['maximum']
            try:
                self.utilization = self.cores_setting['ttheat']/u100ttheat
                self.utilization *= 100
                percent_text = infomation['precent'].format(self.utilization)
            except:
                percent_text = 'NA'
            ##再次演算5s
            self.point_color = ['\'#fff7bf\'', '\'#810000\'']
            for i in range(5):
                next_20tick()
            ##平均数据显示
            self.data_pheat['text'] += infomation['ttinf3'].format(self.pheat)
            self.data_utilization['text'] += infomation['ttinf5'].format(percent_text)
            i = 0
            for coolant_id in self.coolantkeys:
                pfluid = self.pfluid[coolant_id]
                if pfluid != None:
                    fluid = self.cores_setting['fluid'][coolant_id]
                    if fluid == None : fluid = 0
                    if coolant_id == 'molten_thorium_salt':
                        fluid_t = '{}: {} ({}, {}: {})'.format(infomation[coolant_id+'_name'], infomation['core_com15'].format(fluid*20), infomation[coolant_id+'_out'], infomation['core_com16'], infomation['core_com15'].format(pfluid*20))
                        exec('self.fluid_{0}[\'text\'] = fluid_t'.format(coolant_id))
                    else:
                        fluid_t = '{}: {} ({}, {}: {})'.format(infomation[coolant_id+'_name'], infomation['core_com7'].format(fluid), infomation[coolant_id+'_out'], infomation['core_com16'], infomation['core_com7'].format(pfluid))
                        exec('self.fluid_{0}[\'text\'] = fluid_t'.format(coolant_id))
                    exec('self.fluid_{0}.grid(row={1}, column=0, padx=5, pady=1, sticky=NW)'.format(coolant_id,i))
                    i += 1
                else:
                    exec('self.fluid_{0}[\'text\'] = \'\''.format(coolant_id))
                    exec('self.fluid_{0}.grid_forget()'.format(coolant_id))
            #停止后
            self.input_tick = self.tick
            self.draw_all(reform=False, draw=True, dis=True)

        ####开始
        self.tick = input_tick
        self.is_start = True
        self.pause_mid = False
        self.point_color = ['\'#d3d3d3\'', '\'#414141\'']
        self.clr_time_graph(self.tick)
        self.start_b.grid_forget()
        self.pause_b.grid(row=3, column=5, padx=5, pady=5)
        ##存储最原始core_setting
        if self.cores_setting['tttime']==0:
            self.orig_cores_setting = deepcopy(self.cores_setting)
            self.max_heat = self.get_max_heat()
            self.timegraph_setting['max_heat'] = self.max_heat*2 + 1

        self.time_graph.itemconfigure(self.u100text, text=infomation['timeline0'].format(self.max_heat))

        def next_20tick():
            ##存储此时的core_setting
            exec('self.cores_setting_{} = deepcopy(self.cores_setting)'.format(self.tick//20))

            ##绘制
            ###反应堆部分
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        self.set_core_inf((i,j,-1))
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        for k in range(4): self.set_core_inf((i,j,k))
            ###时间轴部分
            heat = self.cores_setting['heat']
            time_s = self.tick//20
            x = (self.tick/self.timegraph_setting['max_time'])*500
            y = (1 - heat/self.timegraph_setting['max_heat'])*300
            exec('self.timepoint{0} = self.time_graph.create_oval({1},{2}-5,{1}+5,{2},fill={3},outline={4},width=2)'.format(time_s, x, y, self.point_color[0], self.point_color[1]))
            ###统计信息部分
            self.updeta_ttinf()
            self.draw_all(reform=False, draw=False, dis=True)

            #非慢化发射中子
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    En, base_id, s = self.cal_emissiom_num((i,j))
                    if base_id == 'core1x1':
                        coolant = all_coolant[self.cores_setting[core_id]['coolant']]
                        if s != None:
                            self.cores_setting[core_id]['rod']['get_neutron'] += s
                        if En != None:
                            self.get_neutron((i-1,j,2), (i,j,-1), En)
                            self.get_neutron((i-1,j,3), (i,j,-1), En)
                            self.get_neutron((i+1,j,0), (i,j,-1), En)
                            self.get_neutron((i+1,j,1), (i,j,-1), En)
                            self.get_neutron((i,j-1,1), (i,j,-1), En)
                            self.get_neutron((i,j-1,3), (i,j,-1), En)
                            self.get_neutron((i,j+1,0), (i,j,-1), En)
                            self.get_neutron((i,j+1,2), (i,j,-1), En)
                        if s != None and En != None:
                            fn = (En * 8) + s
                            maxn = round(all_rods[self.cores_setting[core_id]['rod']['id']]['detail']['maximum']*coolant['maximum'])
                            self.cores_setting[core_id]['rod']['utilization_N'] = fn/maxn
                            if fn > maxn:
                                self.cores_setting[core_id]['rod']['life_multi'] = 4 * (fn/maxn)
                                self.cores_setting[core_id]['rod']['overloaded'] = True
                                if fn > maxn * 2:
                                    self.cores_setting[core_id]['rod']['overloaded2'] = True
                                else:
                                    self.cores_setting[core_id]['rod']['overloaded2'] = False
                            else:
                                self.cores_setting[core_id]['rod']['life_multi'] = 1
                                self.cores_setting[core_id]['rod']['overloaded'] = False
                    elif base_id == 'core2x2':
                        coolant = all_coolant[self.cores_setting[core_id]['coolant']]
                        for k in range(4):
                            if s[k] != None:
                                self.cores_setting[core_id]['rod'][k]['get_neutron'] += s[k]
                            if En[k] != None:
                                if k == 0:
                                    self.get_neutron((i-1,j,2), (i,j,k), En[k])
                                    self.get_neutron((i,j,  2), (i,j,k), En[k])
                                    self.get_neutron((i,j-1,1), (i,j,k), En[k])
                                    self.get_neutron((i,j,  1), (i,j,k), En[k])
                                elif k == 1:
                                    self.get_neutron((i-1,j,3), (i,j,k), En[k])
                                    self.get_neutron((i,j,  3), (i,j,k), En[k])
                                    self.get_neutron((i,j,  0), (i,j,k), En[k])
                                    self.get_neutron((i,j+1,0), (i,j,k), En[k])
                                elif k == 2:
                                    self.get_neutron((i,j,  0), (i,j,k), En[k])
                                    self.get_neutron((i+1,j,0), (i,j,k), En[k])
                                    self.get_neutron((i,j-1,3), (i,j,k), En[k])
                                    self.get_neutron((i,j,  3), (i,j,k), En[k])
                                elif k == 3:
                                    self.get_neutron((i,j,  1), (i,j,k), En[k])
                                    self.get_neutron((i+1,j,1), (i,j,k), En[k])
                                    self.get_neutron((i,j,  2), (i,j,k), En[k])
                                    self.get_neutron((i,j+1,2), (i,j,k), En[k])
                            if s[k] != None and En[k] != None:
                                fn = (En[k] * 4) + s[k]
                                maxn = round(all_rods[self.cores_setting[core_id]['rod'][k]['id']]['detail']['maximum']*coolant['maximum'])
                                self.cores_setting[core_id]['rod'][k]['utilization_N'] = fn/maxn
                                if fn > maxn:
                                    self.cores_setting[core_id]['rod'][k]['life_multi'] = 4 * (fn/maxn)
                                    self.cores_setting[core_id]['rod'][k]['overloaded'] = True
                                    if fn > maxn * 2:
                                        self.cores_setting[core_id]['rod'][k]['overloaded2'] = True
                                    else:
                                        self.cores_setting[core_id]['rod'][k]['overloaded2'] = False
                                else:
                                    self.cores_setting[core_id]['rod'][k]['life_multi'] = 1
                                    self.cores_setting[core_id]['rod'][k]['overloaded'] = False
            ##慢化发射慢化中子
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    En, base_id, s = self.cal_emissiom_num((i,j), True)
                    if base_id == 'core1x1':
                        coolant = all_coolant[self.cores_setting[core_id]['coolant']]
                        if s != None:
                            self.cores_setting[core_id]['rod']['get_neutron_moderated'] += s
                        if En != None:
                            self.get_neutron((i-1,j,2), (i,j,-1), En, True)
                            self.get_neutron((i-1,j,3), (i,j,-1), En, True)
                            self.get_neutron((i+1,j,0), (i,j,-1), En, True)
                            self.get_neutron((i+1,j,1), (i,j,-1), En, True)
                            self.get_neutron((i,j-1,1), (i,j,-1), En, True)
                            self.get_neutron((i,j-1,3), (i,j,-1), En, True)
                            self.get_neutron((i,j+1,0), (i,j,-1), En, True)
                            self.get_neutron((i,j+1,2), (i,j,-1), En, True)
                        if s != None and En != None:
                            fn = (En * 8) + s
                            maxn = round(all_rods[self.cores_setting[core_id]['rod']['id']]['detail']['maximum']*coolant['maximum'])
                            self.cores_setting[core_id]['rod']['utilization_N'] = fn/maxn
                            if fn > maxn:
                                self.cores_setting[core_id]['rod']['life_multi'] = 4 * (fn/maxn) * 4
                                self.cores_setting[core_id]['rod']['overloaded'] = True
                                if fn > maxn * 2:
                                    self.cores_setting[core_id]['rod']['overloaded2'] = True
                                else:
                                    self.cores_setting[core_id]['rod']['overloaded2'] = False
                            else:
                                self.cores_setting[core_id]['rod']['life_multi'] = 1 * 4
                                self.cores_setting[core_id]['rod']['overloaded'] = False
                    elif base_id == 'core2x2':
                        coolant = all_coolant[self.cores_setting[core_id]['coolant']]
                        for k in range(4):
                            if s[k] != None:
                                self.cores_setting[core_id]['rod'][k]['get_neutron_moderated'] += s[k]
                            if En[k] != None:
                                if k == 0:
                                    self.get_neutron((i-1,j,2), (i,j,k), En[k], True)
                                    self.get_neutron((i,j,  2), (i,j,k), En[k], True)
                                    self.get_neutron((i,j-1,1), (i,j,k), En[k], True)
                                    self.get_neutron((i,j,  1), (i,j,k), En[k], True)
                                elif k == 1:
                                    self.get_neutron((i-1,j,3), (i,j,k), En[k], True)
                                    self.get_neutron((i,j,  3), (i,j,k), En[k], True)
                                    self.get_neutron((i,j,  0), (i,j,k), En[k], True)
                                    self.get_neutron((i,j+1,0), (i,j,k), En[k], True)
                                elif k == 2:
                                    self.get_neutron((i,j,  0), (i,j,k), En[k], True)
                                    self.get_neutron((i+1,j,0), (i,j,k), En[k], True)
                                    self.get_neutron((i,j-1,3), (i,j,k), En[k], True)
                                    self.get_neutron((i,j,  3), (i,j,k), En[k], True)
                                elif k == 3:
                                    self.get_neutron((i,j,  1), (i,j,k), En[k], True)
                                    self.get_neutron((i+1,j,1), (i,j,k), En[k], True)
                                    self.get_neutron((i,j,  2), (i,j,k), En[k], True)
                                    self.get_neutron((i,j+1,2), (i,j,k), En[k], True)
                            if s[k] != None and En[k] != None:
                                fn = (En[k] * 4) + s[k]
                                maxn = round(all_rods[self.cores_setting[core_id]['rod'][k]['id']]['detail']['maximum']*coolant['maximum'])
                                self.cores_setting[core_id]['rod'][k]['utilization_N'] = fn/maxn
                                if fn > maxn:
                                    self.cores_setting[core_id]['rod'][k]['life_multi'] = 4 * (fn/maxn) * 4
                                    self.cores_setting[core_id]['rod'][k]['overloaded'] = True
                                    if fn > maxn * 2:
                                        self.cores_setting[core_id]['rod'][k]['overloaded2'] = True
                                    else:
                                        self.cores_setting[core_id]['rod'][k]['overloaded2'] = False
                                else:
                                    self.cores_setting[core_id]['rod'][k]['life_multi'] = 1 * 4
                                    self.cores_setting[core_id]['rod'][k]['overloaded'] = False

            #切换中子
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    self.switch_neutron((i,j))

            ##是否被慢化, 慢化以及取消慢化 moderated
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    has_moderated, base_id = self.check_moderated((i,j))
                    if base_id == 'core1x1':
                        if has_moderated != None:
                            self.cores_setting[core_id]['rod']['moderated'] = has_moderated
                    elif base_id == 'core2x2':
                        for k in range(4):
                            if has_moderated[k] != None:
                                self.cores_setting[core_id]['rod'][k]['moderated'] = has_moderated[k]

            ##检测全体计算慢化倍数
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    multi, base_id = self.cal_multi_num((i,j))
                    if base_id == 'core1x1':
                        if multi != None:
                            self.cores_setting[core_id]['rod']['multi'] = multi
                    elif base_id == 'core2x2':
                        for k in range(4):
                            if multi[k] != None:
                                self.cores_setting[core_id]['rod'][k]['multi'] = multi[k]

            ##耐久计算
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        rod = self.cores_setting[core_id]['rod']
                        if rod != None and rod['active']:
                            if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                self.cores_setting[core_id]['rod']['life'] -= self.cores_setting[core_id]['rod']['life_multi']
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        for k in range(4):
                            rod = self.cores_setting[core_id]['rod'][k]
                            if rod != None and rod['active']:
                                if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                    self.cores_setting[core_id]['rod'][k]['life'] -= self.cores_setting[core_id]['rod'][k]['life_multi']

            ##产热计算
            for i in range(self.core_num):
                for j in range(self.core_num):
                    self.cal_heat((i,j))
            ###更新总产热
            self.cal_all_heat()

            ##流体计算
            for i in range(self.core_num):
                for j in range(self.core_num):
                    self.cal_fluid((i,j))
            ###更新总流体
            self.cal_all_fluid()

            ##每tick计算项
            for tick in range(20):
                #产热
                self.cores_setting['ttheat'] += self.cores_setting['heat']
                #计算增殖棒
                for i in range(self.core_num):
                    for j in range(self.core_num):
                        self.cal_breed((i,j))
                #remeber
                self.tick+=1

            ##检测损坏，转换，严重超载来停止
            for i in range(self.core_num):
                for j in range(self.core_num):
                    core_id = 'core{}_{}'.format(i,j)
                    if self.cores_setting[core_id]['base'] == 'core1x1':
                        rod = self.cores_setting[core_id]['rod']
                        if rod != None and rod['active']:
                            if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                if rod['life'] <= 0:
                                    self.cores_setting[core_id]['rod']['depleted'] = True
                                    self.reset_core_rod((i,j,-1))
                                    self.pause_mid = True
                                if rod['overloaded2']:
                                    self.pause_mid = True
                            if all_rods[rod['id']]['type'] == 'breed_rod':
                                if rod['needed'] <= 0:
                                    self.set_core_rod((i,j,-1), rod_id=all_rods[rod['id']]['detail']['turnto'])
                                    self.draw_core_specific((i,j,-1))
                                    self.pause_mid = True
                    elif self.cores_setting[core_id]['base'] == 'core2x2':
                        for k in range(4):
                            rod = self.cores_setting[core_id]['rod'][k]
                            if rod != None and rod['active']:
                                if all_rods[rod['id']]['type'] == 'fuel_rod' and (not rod['depleted']):
                                    if rod['life'] <= 0:
                                        self.cores_setting[core_id]['rod'][k]['depleted'] = True
                                        self.reset_core_rod((i,j,k))
                                        self.pause_mid = True
                                    if rod['overloaded2']:
                                        self.pause_mid = True
                                if all_rods[rod['id']]['type'] == 'breed_rod':
                                    if rod['needed'] <= 0:
                                        self.set_core_rod((i,j,k), rod_id=all_rods[rod['id']]['detail']['turnto'])
                                        self.draw_core_specific((i,j,k),True)
                                        self.pause_mid = True

            ##时限停止或中途停止
            if self.tick >= self.timegraph_setting['max_time'] and self.is_start:
                self.is_start = False
                self.pause_b.grid_forget()
                self.reset_b.grid(row=3, column=5, padx=5, pady=5)
                ###开始预测
                self.simwin.after(4, predict)
            elif self.pause_mid and self.is_start:
                self.is_start = False
                #停止后
                self.input_tick = self.tick
                self.draw_all(reform=False, draw=True, dis=True)
                self.pause_b.grid_forget()
                self.start_b.grid(row=3, column=5, padx=5, pady=5)
                


            #remeber
            self.cores_setting['tttime'] += 1
            if self.is_start:
                self.simwin.after(5, next_20tick)
        ##########
        if self.is_start:
            next_20tick()


    def pause_sim(self):
        self.is_start = False
        self.draw_all(reform=False, draw=True, dis=True)
        self.pause_b.grid_forget()
        self.start_b.grid(row=3, column=5, padx=5, pady=5)

    def stop_sim(self, input_tick):
        self.pause_sim()
        self.input_tick = 0
        self.clr_time_graph()
        self.draw_all(reform=False, draw=True, dis=True)
        self.timegraph_setting['max_heat'] = self.get_max_heat()*2 + 1
        self.updeta_ttinf()
        self.reset_b.grid_forget()
        self.start_b.grid(row=3, column=5, padx=5, pady=5)

    def reset_sim(self):
        self.is_start = False
        self.clr_time_graph()
        self.input_tick = 0
        self.cores_setting = deepcopy(self.orig_cores_setting)
        self.draw_all(reform=True, draw=True, dis=True)
        self.timegraph_setting['max_heat'] = self.get_max_heat()*2 + 1
        self.updeta_ttinf()
        self.reset_b.grid_forget()
        self.start_b.grid(row=3, column=5, padx=5, pady=5)

    ####切换反应堆状态
    def change_time(self, event):
        sel_time = (event.x/500)*self.timegraph_setting['max_time']
        sel_time_s = round(sel_time/20)
        simed_time_s = self.tick//20
        if sel_time_s < simed_time_s:
            x = ((sel_time_s*20)/self.timegraph_setting['max_time'])*500+2
            self.time_graph.coords(self.selline, (x,0,x,300))
            self.time_graph.itemconfigure(self.selline,fill='#c8c8c8')
            exec('self.cores_setting = deepcopy(self.cores_setting_{})'.format(sel_time_s))
            self.draw_all(reform=True, draw=True, dis=True)
            my_event = fake_event(*GetCursorPos())
            self.Balloon_show(my_event,msg=infomation['time_graph'])
            self.updeta_ttinf()
            self.input_tick = sel_time_s*20
            self.pause_b.grid_forget()
            self.reset_b.grid_forget()
            self.start_b.grid_forget()
            if sel_time_s < self.timegraph_setting['max_time']//20:
                self.start_b.grid(row=3, column=5, padx=5, pady=5)
            else:
                self.reset_b.grid(row=3, column=5, padx=5, pady=5)
            
######################################
    def debug(self, event):
        print(self.cores_setting['core0_0']['core_inf'])

    def test_bind(self, event, pos):
        print(event)
        print(event.x, event.y)
        print('左键{}'.format(pos))

    @staticmethod
    def heat2col(heat):
        midheat = 1000
        color_num = floor((heat/(midheat+heat))*255*2)
        B = 0
        if color_num <= 255:
            R = color_num
            G = 255
        else:
            R = 255
            G = 255 - (color_num-255)
        return '#{:0<2x}{:0<2x}{:0<2x}'.format(R,G,B)

    @staticmethod
    def fluid2col(fluid):
        midfluid = 100
        color_num = floor((fluid/(midfluid+fluid))*(255+135))
        B = 255
        if color_num <= 135:
            R = 0
            G = color_num + 120
        else:
            R = (color_num-135)
            G = 255
        return '#{:0<2x}{:0<2x}{:0<2x}'.format(R,G,B)

    @staticmethod
    def uti2col(utilization_N):
        if utilization_N > 1:
            R,G,B = 255,60,60
        else:
            R,G,B = 255,255,255
        return '#{:0<2x}{:0<2x}{:0<2x}'.format(R,G,B)



    @staticmethod
    def functionAdaptor(fun,**kwds):
        return lambda event,fun=fun,kwds=kwds:fun(event,**kwds)

    @staticmethod
    def functionAdaptor_b(fun,**kwds):
        return lambda fun=fun,kwds=kwds:fun(**kwds)

    @staticmethod
    def test_bind1(event, pos):
        print('右键{}'.format(pos))


    @staticmethod
    def test_bind2(pos):
        print('A{}'.format(pos))

class fake_event:
    def __init__(self, x_root, y_root):
        self.x_root = x_root
        self.y_root = y_root

def _test():
    m = main()
    m.simwin.mainloop()

if __name__ == "__main__":
    _test()
