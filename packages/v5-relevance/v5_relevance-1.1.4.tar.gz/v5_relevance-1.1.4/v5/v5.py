"""
V5版相关度算法类
从unified_interface.py中提取的V5算法，封装为独立的类
适合发布到PyPi的标准版本
"""

import os

# 导入jieba库 - 标准PyPi依赖方式
try:
    import jieba
    import jieba.posseg as pseg
except ImportError:
    raise ImportError(
        "jieba库未安装，请使用以下命令安装：\n"
        "pip install jieba\n"
        "或者安装完整版本：\n"
        "pip install v5-relevance[full]"
    )


class V5Relev:
    """V5版相关度算法类"""
    
    def __init__(self, user_dict_path="user_dict.txt", debug=False):
        """初始化V5算法类
        
        Args:
            user_dict_path: 用户自定义词典路径
        """
        self.debug = debug
        self.user_dict_path = user_dict_path
        self.jieba = jieba
        self.pseg = pseg
        self._ensure_user_dict()
        self._load_jieba_dict()
        

    # 格式化输出
    def print_format(self, message:str):
        """自定输出样式"""
        if self.debug == True:
            print("--- [V5] ---: " + message)
        else:
            pass
       
    def _ensure_user_dict(self):
        """确保用户词典文件存在，如果不存在则创建并写入测试数据"""
        if os.path.exists(self.user_dict_path):
            return
        
        print(f"[INFO] 用户词典文件 {self.user_dict_path} 不存在，正在创建...")
        
        # 创建默认的用户词典内容
        default_dict_content = """# 人名和地名
元龙居士 3 nr
元龙驿 5 nt
张三 3 nr
李四 3 nr
北京 3 ns
上海 3 ns
深圳 3 ns
杭州 3 ns
中国 3 ns

# 专业术语
LLM 5 n
API_KEY 5 n
BASE_URL 5 n
MySQL 5 n
SQLite 5 n
MSSQL 5 n
全文搜索 4 n
jieba 5 n
langchain 5 n
langgraph 5 n
embedding 5 n
vectorstore 5 n
RAG 5 n
token 5 n
prompt 4 n
context 4 n
pipeline 4 n
session 4 n
agent 4 n
document 4 n
schema 4 n
node 4 n
graph 4 n
workflow 4 n
MCP 4 n

# 自定义开发
lmcp 5 n
元龙记事本 5 n
文件探索问答 5 n
文件检索问答 5 n

# 常用缩写
AI 5 n
API 5 n
URL 5 n
HTTP 5 n
HTTPS 5 n
UI 4 n
UX 4 n
DB 4 n
SQL 4 n
CLI 4 n
SDK 4 n
GPU 4 n
CPU 4 n
RAM 4 n
JSON 4 n
YAML 4 n
XML 4 n

# 技术名词
OpenAI 5 n
DeepSeek 5 n
Ollama 5 n
ChatGPT 5 n
GPT 5 n
Python 5 n
JavaScript 5 n
TypeScript 5 n
HTML 5 n
CSS 5 n
C# 5 n
C++ 5 n
Java 5 n
Linux 5 n
Ubuntu 5 n
Windows 5 n
Docker 5 n
Kubernetes 5 n
VSCode 5 n
GitHub 5 n
GitLab 5 n
Flask 5 n
FastAPI 5 n
Django 5 n
Pandas 5 n
NumPy 5 n
TensorFlow 5 n
PyTorch 5 n
requests 4 n
asyncio 4 n
threading 4 n
multiprocessing 4 n
subprocess 4 n
sys 4 n
os 4 n
pathlib 4 n
re 4 n
json 4 n
logging 4 n

# 时间相关
今天 2 t
明天 2 t
昨天 2 t
上午 2 t
下午 2 t
晚上 2 t
本周 2 t
下周 2 t
本月 2 t
去年 2 t
今年 2 t
明年 2 t

# 常见问题关键词
天气 2 n
时间 2 n
日期 2 n
帮助 2 n
配置 2 n
注册 2 n
登录 2 n
教程 2 n
示例 2 n
错误 2 n
更新 2 n
版本 2 n
安装 2 n
卸载 2 n
权限 2 n
"""
        
        try:
            with open(self.user_dict_path, 'w', encoding='utf-8') as f:
                f.write(default_dict_content)
            print(f"[INFO] 已创建默认用户词典文件 {self.user_dict_path}")
        except Exception as e:
            print(f"[WARN] 创建用户词典文件失败: {e}")
    
    def _load_jieba_dict(self):
        """加载自定义jieba词典"""
        try:
            # 优先级1：当前目录
            if os.path.exists(self.user_dict_path):
                self.jieba.load_userdict(self.user_dict_path)
                # print(f"[INFO] 已从 {self.user_dict_path} 加载自定义分词词典")
                self.print_format(f'[INFO] 已从 {self.user_dict_path} 加载自定义分词词典')
                return
            
            # 优先级2：_internal目录
            internal_path = os.path.join("_internal", self.user_dict_path)
            if os.path.exists(internal_path):
                self.jieba.load_userdict(internal_path)
                # print(f"[INFO] 已从 _internal/{self.user_dict_path} 加载自定义分词词典")
                self.print_format(f'[INFO] 已从 _internal/{self.user_dict_path} 加载自定义分词词典')
                return
            
            # print(f"[WARN] 未找到自定义词典文件 {self.user_dict_path}，使用默认分词")
            self.print_format(f"[WARN] 未找到自定义词典文件 {self.user_dict_path}，使用默认分词")
            
        except Exception as e:
            self.print_format(f"[WARN] 分词词典加载异常，使用默认分词: {e}")
    
    def extract_core_keywords(self, tokens):
        """提取核心关键词，基于jieba词性标注过滤停用词"""
        core_keywords = []
        for token in tokens:
            # 使用jieba词性标注来判断词性
            words = list(self.pseg.cut(token))
            if words:
                word, pos = words[0]
                # 过滤停用词词性：疑问代词、助词、连词、介词、语气词、叹词
                # 排除'eng'（英文）和'x'（未知词性），这些可能是英文单词
                if pos.startswith(('r', 'u', 'c', 'p', 'y')) or (pos.startswith('e') and pos != 'eng'):
                    continue
                # 过滤单字词（除非是英文单词或数字）
                if len(token) <= 1 and not (token.isalpha() or token.isdigit()):
                    continue
                # 保留其他词性的词
                core_keywords.append(token)
            else:
                # 如果无法识别词性，保留长度大于1的词
                if len(token) > 1:
                    core_keywords.append(token)
        return core_keywords
    
    def extract_content_words(self, tokens):
        """提取内容关键词（名词、动词等实词）"""
        content_words = []
        for token in tokens:
            # 使用jieba词性标注来判断词性
            words = list(self.pseg.cut(token))
            if words:
                word, pos = words[0]
                # 核心实词：名词、动词、形容词
                if pos.startswith(('n', 'v', 'a')):
                    content_words.append(token)
                # 其他实词：副词、数词、量词、代词（长度大于1）
                elif pos.startswith(('d', 'm', 'q', 'r')) and len(token) > 1:
                    content_words.append(token)
                # 英文单词（eng词性）和数字（长度大于1）
                elif pos == 'eng' or ((token.isalpha() or token.isdigit()) and len(token) > 1):
                    content_words.append(token)
                # 未知词性（x）但可能是英文单词
                elif pos == 'x' and len(token) > 1:
                    content_words.append(token)
        
        return content_words
    
    def filter_tokens_with_pos(self, tokens):
        """使用jieba词性标注进行智能分词过滤"""
        filtered_tokens = []
        for token in tokens:
            # 先去除空格，但保留非空格字符
            token = token.strip()
            if not token:
                continue
            
            # 使用jieba词性标注来判断词性
            words = list(self.pseg.cut(token))
            if words:
                word, pos = words[0]
                # 过滤停用词词性：助词、连词、介词、语气词、叹词等
                # 排除'eng'（英文）和'x'（未知词性），这些可能是英文单词
                if pos.startswith(('u', 'c', 'p', 'y')) or (pos.startswith('e') and pos != 'eng'):
                    continue
                # 保留其他词性的词，包括单字词
                filtered_tokens.append(token.lower())
            else:
                # 如果无法识别词性，保留长度大于0的词
                if len(token) > 0:
                    filtered_tokens.append(token.lower())
        
        return filtered_tokens
    
    def get_token_weight(self, token):
        """根据词性分配权重（使用jieba词性标注）"""
        # 使用jieba词性标注来判断词性
        words = list(self.pseg.cut(token))
        if words:
            word, pos = words[0]
            
            # 英文单词（eng）和未知词性（x）给予较高权重
            if pos == 'eng' or pos == 'x':
                return 0.7
            
            # 核心关键词：名词、动词、形容词
            if pos.startswith(('n', 'v', 'a')):
                return 1.0
            
            # 次要关键词：副词、数词、量词、代词
            elif pos.startswith(('d', 'm', 'q', 'r')):
                return 0.5
            
            # 停用词：介词、连词、助词、语气词、叹词（排除'eng'）
            elif pos.startswith(('p', 'c', 'u', 'y')) or (pos.startswith('e') and pos != 'eng'):
                return 0.1
            
            # 其他词性：默认权重
            else:
                return 0.5
        
        # 如果无法识别词性，根据长度和内容判断
        if len(token) <= 1:
            return 0.1  # 单字词权重较低
        elif token.isdigit():
            return 0.3  # 数字权重中等
        elif token.isalpha():
            return 0.7  # 英文单词权重较高
        else:
            return 0.5  # 默认权重
    
    # 用于计算某关键词名在目标文本中的相关度评分
    def calculate_relevance_score(self, content, query, user_id=None):
        """
        **用于计算某关键词名在目标文本中的相关度评分**

        V5版相关度算法：总匹配度 = LIKE匹配 + 标题关键词匹配 + 关键词紧密度 + 内容匹配平均占比
        
        Args:
            content: 待匹配的文本内容
            query: 用户问题/查询词
            user_id: 用户ID（可选，用于个性化计算）
            
        Returns:
            相关度评分（浮点数）
        """
        
        # if self.debug == True:
        #     print('\n................................................')
        
        if not content:
            return 0.0
        
        # 预处理内容
        clean_content = content.replace('\n', ' ').strip()
        clean_content_lower = clean_content.lower()
        query_lower = query.lower()
        
        # 使用jieba分词
        key_tokens = list(self.jieba.cut(query))
        
        # 使用jieba词性标注进行智能分词过滤
        filtered_tokens = self.filter_tokens_with_pos(key_tokens)
        
        key_tokens = filtered_tokens
        
        if not key_tokens:
            return 0.0
        
        # 1. LIKE匹配度计算
        like_score = 0.0
        
        # 1.1 精确相等匹配
        if clean_content_lower == query_lower:
            like_score = 100.0
        
        # 1.2 标题开头匹配
        title_part = clean_content_lower[:100] if len(clean_content_lower) > 100 else clean_content_lower
        title_without_markers = title_part.replace('#', '').strip()
        
        if title_without_markers.startswith(query_lower):
            like_score = 90.0
        
        # 1.3 连续关键词匹配
        elif like_score == 0.0:
            core_keywords = self.extract_core_keywords(key_tokens)
            if core_keywords:
                joined_keywords = ''.join(core_keywords)
                if joined_keywords in title_without_markers:
                    like_score = 80.0
        
        # 确保core_keywords变量已定义
        if 'core_keywords' not in locals():
            core_keywords = self.extract_core_keywords(key_tokens)
        
        # 1.4 完整包含匹配
        if like_score == 0.0 and query_lower in clean_content_lower:
            like_score = 60.0
        
        # 2. 标题关键词匹配
        title_part = clean_content_lower[:50] if len(clean_content_lower) > 50 else clean_content_lower
        content_words = self.extract_content_words(key_tokens)
        title_match_count = sum(1 for word in content_words if word in title_part)
        
        # 3. 内容匹配平均占比
        content_length = len(clean_content_lower)
        if content_length == 0:
            content_length = 1
        
        total_weighted_percentage = 0.0
        total_weight = 0.0
        
        for token in key_tokens:
            token_count = clean_content_lower.count(token)
            if token_count > 0:
                percentage = token_count / content_length
                weight = self.get_token_weight(token)
                total_weighted_percentage += percentage * weight
                total_weight += weight
        
        weighted_content_match_avg = total_weighted_percentage / total_weight if total_weight > 0 else 0.0
        
        # 4. 关键词紧密度
        keyword_proximity_score = 0.0
        if core_keywords and len(core_keywords) > 1:
            keyword_positions = {}
            for keyword in core_keywords:
                pos = title_without_markers.find(keyword)
                if pos != -1:
                    keyword_positions[keyword] = pos
            
            if len(keyword_positions) >= 2:
                min_distance = float('inf')
                keywords_list = list(keyword_positions.keys())
                
                for i in range(len(keywords_list)):
                    for j in range(i+1, len(keywords_list)):
                        pos1 = keyword_positions[keywords_list[i]]
                        pos2 = keyword_positions[keywords_list[j]]
                        distance = abs(pos1 - pos2)
                        if distance < min_distance:
                            min_distance = distance
                
                max_possible_distance = len(title_without_markers)
                if max_possible_distance > 0:
                    normalized_distance = min_distance / max_possible_distance
                    keyword_proximity_score = 15 * (1 - normalized_distance)
        
        # 5. 总分数计算
        total_score = like_score + title_match_count * 3 + keyword_proximity_score + weighted_content_match_avg
        
        total_score_last = round(total_score, 4)
        # self.print_format(f'[SINGLE] 相关度分数: {total_score_last}')
        return total_score_last
    
    # 获取某关键词句相对目标文本列表中，相关度排序的前N条记录并进行大小控制
    def get_top_relevant_notes(self, notes, query:str, limit=10, sort_desc=True, max_chars=70000):
        """获取某关键词句相对目标文本列表中，相关度排序的前N条记录 - 统一使用V5算法计算分数，并进行大小控制
        
        Args:
            notes: 笔记列表，可以是3参数或4参数格式 list(tuple)
            query: 查询词
            limit: 返回结果数量限制
            sort_desc: 是否按降序排序，默认True（降序），False为升序
            max_chars: 最大字符数限制，用于控制返回结果的总大小，默认70000
            
        Returns:
            按相关度排序的笔记列表（默认降序），并且总字符数不超过max_chars
        """
        self.print_format(f'[START] ----------------------------------------------------')
        scored_notes = []
        
        for note in notes:
            # 统一处理3参数和4参数输入，确保分数只来自V5算法
            if len(note) == 3:
                # 3参数格式：(note_id, content, created_at)
                note_id, content, created_at = note
                # 使用V5算法计算相关度分数
                score = self.calculate_relevance_score(content, query)
            elif len(note) == 4:
                # 4参数格式：(note_id, content, created_at, score)
                note_id, content, created_at, existing_score = note
                # 忽略已有的分数，统一使用V5算法重新计算
                score = self.calculate_relevance_score(content, query)
            else:
                raise ValueError(f"--- [V5] ---: [ERR] 搜索结果结构异常，期望3或4参数，实际得到{len(note)}个参数: {note}")
            
            # 构建新的结果元组，包含相关度分数
            scored_notes.append((note_id, content, created_at, score))
        
        # 按相关度排序，根据sort_desc参数决定升序/降序
        scored_notes.sort(key=lambda x: x[-1], reverse=sort_desc)

        # 进行大小控制
        # # 计算总字符数，如果超过max_chars则删除评分最低的记录，直到总字符数不超过max_chars
        # total_chars = sum(len(content) for _, content, _, _ in scored_notes)
        # self.print_format(f'[INFO] 当前记录大小：{total_chars}')
        
        # # 循环删除评分最低的记录，直到总字符数不超过max_chars或者只剩下最后一条记录，如果最后记录仍然大于max_chars，正常返回这条记录，但打印警告
        # while total_chars > max_chars and scored_notes:
        #     # 找到评分最低的记录（由于已经排序，如果sort_desc=True，最低分在末尾；如果sort_desc=False，最低分在开头）
        #     # 为了更通用，我们总是找到分数最小的记录
        #     min_score_index = min(range(len(scored_notes)), key=lambda i: scored_notes[i][-1])
        #     self.print_format(f'[WARN] 记录大于预定值 {max_chars} ,删除评分最低的记录序号 {min_score_index}')
        #     removed_note = scored_notes.pop(min_score_index)
        #     total_chars -= len(removed_note[1])
        #     self.print_format(f'[INFO] 当前记录大小：{total_chars}')


        # 进行大小控制
        content_index = 1
        score_index = -1

        total_chars = sum(len(note[content_index]) for note in scored_notes)
        self.print_format(f"[INFO] 初始字符数: {total_chars}, 记录数: {len(scored_notes)}")

        # 循环删除最低评分记录
        while total_chars > max_chars and len(scored_notes) > 1:
            # 找到评分最低的记录索引
            min_index = min(
                range(len(scored_notes)),
                key=lambda i: scored_notes[i][score_index]
            )

            removed = scored_notes.pop(min_index)
            removed_chars = len(removed[content_index])
            total_chars -= removed_chars

            self.print_format(
                f"[WARN] 总字符数超出 {max_chars}, "
                f"删除评分最低的记录 index={min_index}, "
                f"score={removed[score_index]}, "
                f"chars={removed_chars}"
            )
            self.print_format(f"[INFO] 当前总字符数: {total_chars}，记录数：{len(scored_notes)}")

        # 只剩最后一条但仍超限
        if len(scored_notes) == 1:
            last_len = len(scored_notes[0][content_index])
            if last_len > max_chars:
                self.print_format(
                    f"[WARN] 仅剩最后一条记录，字符数 {last_len} "
                    f"仍大于限制 {max_chars}，但仍然保留"
                )
                if self.debug == False:
                    print(f'--- [V5] ---: [WARN] 由于大小限制策略，仅保留查询到的相关度最高的一条记录，字符数 {last_len} 虽然大于限制 {max_chars}，但仍然保留')


        # 返回前limit条记录
        self.print_format(f'[INFO] 最后结果集：{scored_notes}')
        self.print_format(f'[END] ------------------------------------------------------\n')


        return scored_notes[:limit]


# 使用示例
if __name__ == "__main__":
    # 创建V5算法实例
    v5 = V5Relev(debug=True)
    
    # 测试相关度计算
    content = "markdown是一个广泛使用于AI和人类写作的文档格式，它有很好的前景"
    query = "markdown"
    
    score = v5.calculate_relevance_score(content, query)
    print(f"相关度分数: {score}")
    
    # 测试批量处理
    notes = [
        (1, "AI软件前端设计哲学", "2025-10-30"),
        (2, "AI软件设计白皮书", "2025-10-29"), 
        (3, "从AI软件输入中使用markdown格式就可以知道markdown的重要性", "2025-10-28")
    ]
    
    # 测试降序（默认）
    top_notes_desc = v5.get_top_relevant_notes(notes, query, limit=2, sort_desc=True, max_chars=10)
    print(f"降序排列:\n{top_notes_desc}")
    for note in top_notes_desc:
        print(f"  ID: {note[0]}, 分数: {note[3]}")
    
    top_notes_asc = v5.get_top_relevant_notes(notes, query, limit=2, sort_desc=False, max_chars=10)
    print(f"升序排列:\n{top_notes_asc}")
    for note in top_notes_asc:
        print(f"  ID: {note[0]}, 分数: {note[3]}")

