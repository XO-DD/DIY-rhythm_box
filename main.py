#目前还有很多严重的bug,希望大家帮我改一改
import pygame
import os
import json
import zipfile
import sys
from pygame import mixer

# 初始化pygame
pygame.init()
mixer.init()

# 屏幕设置
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("节奏盒子")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
HIGHLIGHT = (200, 200, 255, 150)
SLOT_COLOR = (50, 50, 70, 100)

# 布局参数
BG_HEIGHT = 300
CHAR_SIZE = (95, 145)
SLOT_COLS = 7
SLOT_SPACING = 10
SLOT_START_Y = 320

class Character:
    def __init__(self, name, folder_path):
        self.name = name
        self.folder_path = folder_path
        self.logo = None
        self.logo_dark = None
        self.frames = []
        self.music1 = None
        self.music2 = None
        self.load_resources()
    
    def load_resources(self):
        try:
            self.logo = pygame.image.load(os.path.join(self.folder_path, "logo.png")).convert_alpha()
            self.logo_dark = self.logo.copy()
            self.logo_dark.fill(GRAY, special_flags=pygame.BLEND_MULT)
            
            self.music1 = os.path.join(self.folder_path, "music1.wav")
            self.music2 = os.path.join(self.folder_path, "music2.wav")
            
            pngs_json = os.path.join(self.folder_path, "pngs.json")
            if os.path.exists(pngs_json):
                with open(pngs_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('frames', []):
                        img_path = os.path.join(self.folder_path, "pngs", item['name'])
                        if os.path.exists(img_path):
                            img = pygame.image.load(img_path).convert_alpha()
                            img = pygame.transform.scale(img, CHAR_SIZE)
                            self.frames.append({
                                'image': img,
                                'time': item.get('time', 0.5)
                            })
        except Exception as e:
            print(f"加载角色 {self.name} 资源失败: {e}")

class GameState:
    def __init__(self, char_count):
        self.slot_count = 7  # 固定为7个槽位
        self.char_slots = [None] * self.slot_count
        self.playing_index = -1
        self.current_frame = 0
        self.frame_time = 0
        self.last_update = 0
        self.music_playing = False
        self.music_part = 1
        self.dragging = None
        self.drag_offset = (0, 0)
        
        # 设置7个槽位的坐标
        self.slot_rects = [
            pygame.Rect(100, 152, CHAR_SIZE[0], CHAR_SIZE[1]),
            pygame.Rect(200, 152, CHAR_SIZE[0], CHAR_SIZE[1]),
            pygame.Rect(300, 152, CHAR_SIZE[0], CHAR_SIZE[1]),
            pygame.Rect(400, 152, CHAR_SIZE[0], CHAR_SIZE[1]),
            pygame.Rect(500, 152, CHAR_SIZE[0], CHAR_SIZE[1]),
            pygame.Rect(600, 152, CHAR_SIZE[0], CHAR_SIZE[1]),
            pygame.Rect(700, 152, CHAR_SIZE[0], CHAR_SIZE[1])
        ]

def load_resources():
    resources = {
        'bg': None,
        'frame': None,
        'done_img': None,
        'again_img': None,
        'characters': [],
        'error': False
    }
    
    if not os.path.exists("data"):
        if os.path.exists("data.zip"):
            try:
                with zipfile.ZipFile("data.zip", 'r') as zip_ref:
                    zip_ref.extractall("data")
            except:
                resources['error'] = True
                return resources
        else:
            resources['error'] = True
            return resources
    
    try:
        resources['bg'] = pygame.image.load(os.path.join("data", "bg.png")).convert()
        resources['frame'] = pygame.transform.scale(
            pygame.image.load(os.path.join("data", "k.png")).convert_alpha(),
            (WIDTH, BG_HEIGHT)
        )
        resources['done_img'] = pygame.transform.scale(
            pygame.image.load(os.path.join("data", "done.png")).convert_alpha(),
            CHAR_SIZE
        )
        resources['again_img'] = pygame.image.load(os.path.join("data", "again.png")).convert_alpha()
        
        with open(os.path.join("data", "c.txt"), 'r') as f:
            for line in f:
                char_name = line.strip()
                if char_name and os.path.exists(os.path.join("data", char_name)):
                    resources['characters'].append(Character(char_name, os.path.join("data", char_name)))
    except Exception as e:
        print(f"资源加载错误: {e}")
        resources['error'] = True
    
    return resources

def main():
    resources = load_resources()
    if resources['error']:
        print("资源加载失败！")
        return
    
    game_state = GameState(len(resources['characters']))
    clock = pygame.time.Clock()
    running = True
    
    # 计算角色图标的布局
    icon_size = 32
    icon_spacing = 10
    icons_per_row = (WIDTH - 20) // (icon_size + icon_spacing)
    icon_start_y = 300
    icon_start_x = (WIDTH - (icons_per_row * (icon_size + icon_spacing))) // 2
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # 允许拖动所有角色，移除对 playing_index 的限制
                for idx, char in enumerate(resources['characters']):
                    row = idx // icons_per_row
                    col = idx % icons_per_row
                    logo_rect = pygame.Rect(
                        icon_start_x + col * (icon_size + icon_spacing),
                        icon_start_y + row * (icon_size + icon_spacing),
                        icon_size, icon_size
                    )
                    if logo_rect.collidepoint(mouse_pos):  # 移除对 playing_index 的限制，允许拖动所有图标
                        game_state.dragging = idx
                        game_state.drag_offset = (
                            mouse_pos[0] - logo_rect.x,
                            mouse_pos[1] - logo_rect.y
                        )
                
                for i, slot_rect in enumerate(game_state.slot_rects):
                    if i < len(game_state.char_slots) and slot_rect.collidepoint(mouse_pos) and game_state.playing_index == i:
                        game_state.playing_index = -1  # 停止当前演奏
                        mixer.music.stop()  # 停止音乐播放
                        game_state.music_playing = False  # 设置音乐播放状态为False
                        game_state.char_slots[i] = None  # 角色停止演奏后变回空角色
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and game_state.dragging is not None:
                for i, slot_rect in enumerate(game_state.slot_rects):
                    if i < len(game_state.char_slots) and slot_rect.collidepoint(pygame.mouse.get_pos()):
                        game_state.char_slots[i] = game_state.dragging
                        game_state.playing_index = i
                        game_state.current_frame = 0
                        game_state.frame_time = 0
                        try:
                            mixer.music.load(resources['characters'][game_state.dragging].music1)
                            mixer.music.play()
                            game_state.music_playing = True
                            game_state.music_part = 1
                            game_state.last_update = pygame.time.get_ticks()
                            # 放置角色时的变化效果
                            char = resources['characters'][game_state.dragging]
                            if char.frames:
                                game_state.current_frame = len(char.frames) - 1  # 显示最后一帧作为变化效果
                        except:
                            game_state.playing_index = -1
                game_state.dragging = None
        
        if game_state.playing_index != -1 and game_state.playing_index < len(game_state.char_slots):
            char_idx = game_state.char_slots[game_state.playing_index]
            if char_idx is not None and char_idx < len(resources['characters']):
                char = resources['characters'][char_idx]
                current_time = pygame.time.get_ticks()
                elapsed = (current_time - game_state.last_update) / 1000.0
                
                if game_state.current_frame < len(char.frames):
                    game_state.frame_time += elapsed
                    
                    if game_state.frame_time >= char.frames[game_state.current_frame]['time']:
                        game_state.frame_time = 0
                        game_state.current_frame += 1
                        
                        if game_state.current_frame >= len(char.frames):
                            if game_state.music_part == 1:
                                try:
                                    mixer.music.load(char.music2)
                                    mixer.music.play()
                                    game_state.music_part = 2
                                    game_state.current_frame = 0
                                except:
                                    game_state.playing_index = -1
                            else:
                                # 音乐播放结束后自动切换到下一个角色
                                game_state.playing_index = (game_state.playing_index + 1) % len(game_state.char_slots)
                                if game_state.char_slots[game_state.playing_index] is not None:
                                    try:
                                        mixer.music.load(resources['characters'][game_state.char_slots[game_state.playing_index]].music1)
                                        mixer.music.play()
                                        game_state.music_part = 1
                                        game_state.current_frame = 0
                                        game_state.last_update = pygame.time.get_ticks()
                                    except:
                                        game_state.playing_index = -1
                                else:
                                    game_state.playing_index = -1
                
                game_state.last_update = current_time
                
                if not mixer.music.get_busy() and game_state.music_playing:
                    if game_state.music_part == 1:
                        try:
                            mixer.music.load(char.music2)
                            mixer.music.play()
                            game_state.music_part = 2
                            game_state.current_frame = 0
                        except:
                            game_state.playing_index = -1
                    else:
                        # 音乐播放结束后自动切换到下一个角色
                        game_state.playing_index = (game_state.playing_index + 1) % len(game_state.char_slots)
                        if game_state.char_slots[game_state.playing_index] is not None:
                            try:
                                mixer.music.load(resources['characters'][game_state.char_slots[game_state.playing_index]].music1)
                                mixer.music.play()
                                game_state.music_part = 1
                                game_state.current_frame = 0
                                game_state.last_update = pygame.time.get_ticks()
                            except:
                                game_state.playing_index = -1
                        else:
                            game_state.playing_index = -1

        # 渲染
        screen.blit(resources['bg'], (0, 0))
        screen.blit(resources['frame'], (0, 300))  # 框架在背景下面
        
        for i, slot_rect in enumerate(game_state.slot_rects):
            if i >= len(game_state.char_slots):
                continue
            
            slot_surface = pygame.Surface((slot_rect.width, slot_rect.height), pygame.SRCALPHA)
            slot_surface.fill(SLOT_COLOR)
            screen.blit(slot_surface, (slot_rect.x, slot_rect.y))
            
            if game_state.char_slots[i] is not None and game_state.char_slots[i] < len(resources['characters']):
                char = resources['characters'][game_state.char_slots[i]]
                if game_state.playing_index == i and char.frames:
                    if game_state.current_frame < len(char.frames):
                        screen.blit(char.frames[game_state.current_frame]['image'], (slot_rect.x, slot_rect.y))
                elif char.frames:
                    screen.blit(char.frames[0]['image'], (slot_rect.x, slot_rect.y))
            else:
                screen.blit(resources['done_img'], (slot_rect.x, slot_rect.y))  # 空角色在背景上面
        
        # 渲染所有角色
        for idx, char in enumerate(resources['characters']):
            row = idx // icons_per_row
            col = idx % icons_per_row
            pos = (
                icon_start_x + col * (icon_size + icon_spacing),
                icon_start_y + row * (icon_size + icon_spacing)
            )
            if game_state.dragging == idx:
                pos = (
                    pygame.mouse.get_pos()[0] - game_state.drag_offset[0],
                    pygame.mouse.get_pos()[1] - game_state.drag_offset[1]
                )
            
            if idx not in game_state.char_slots or game_state.playing_index == -1:
                logo = char.logo_dark if idx in game_state.char_slots else char.logo
                screen.blit(logo, pos)
                
                if idx == game_state.dragging:
                    highlight = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                    highlight.fill(HIGHLIGHT)
                    screen.blit(highlight, pos)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
