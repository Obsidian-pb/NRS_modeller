#%%
import logging
logger = logging.getLogger('NRS')


class NRS_Revision(object):
    '''
    Класс ревизии элементов НРС. Содержит инструментальные функции анализа элементов НРС.
    '''

    @staticmethod
    def print_previous_elements(elmnt):
        '''
        Печать перечня элементов подключенных к elmnt
            Вход:
                elmnt: Element. Элемент НРС для которого следует вывести перечень подключенных элементов
        '''
        elmnts = []
        for child in elmnt.elements_previous:
            elmnts.append(child.name)
        print(','.join(elmnts))

    @staticmethod
    def print_next_elements(elmnt):
        '''
        Печать перечня элементов к которым подключен elmnt
            Вход:
                elmnt: Element. Элемент НРС для которого следует вывести перечень элементов к которым он подключен
        '''
        elmnts = []
        for child in elmnt.elements_next:
            elmnts.append(child.name)
        print(','.join(elmnts))

    @staticmethod
    def print_element_state(elmnt, e_keys=None):
        '''
        Печать всех значений параметров elmnt
            Вход:
                `elmnt`: Element 
                    Element. Элемент НРС для которого следует вывести перечень параметров
                `e_keys`: None | list
                    Список параметров которые следует распечатать. Если не указан, печатаются все.
        '''
        if e_keys is None:
            e_keys = list(elmnt.__dict__.keys())

        for i in e_keys:
            try:
                v = elmnt.__dict__[i]
                try:
                    print(i + ": " + str(v))
                except:
                    print(i + ": не строчный тип")
            except KeyError:
                print(f'Параметр {i} не существует.')

    @staticmethod
    def calc_p(q, H):      
        '''
        Функция возвращает проводимость насадка:
            Вход:
                q - производительность ствола\n
                H - напор при котором ствол имеет производительность q\n
            Пример:
                ```
                calc_p(3.7, 40)
                >>>0.5850213671311502
                ```
        '''
        return q/pow(H, 0.5)
    
    @staticmethod
    def calc_h(n,s,q):
        '''
        Функция возвращает потерю напора:

        # Вход

        n - количество рукавов

        s - гидравлическое сопротивление 1 пожарного рукава

        q - Расход воды через сечение рукава

        # Пример
            ```
            calc_h(6, 0.13, 7.4)
            >>>42.71280000000001
            ```
        '''
        return n*s*(q**2)


    @staticmethod
    def print_model_elements(model):
        '''Печать всех элементов содержащихся в модели'''
        print("all:")
        for elmnt in model.elmnts:
            print("  " + elmnt.name)
        print("in:")
        for elmnt in model.elmnts_in:
            print("  " + elmnt.name)
        print("out:")
        for elmnt in model.elmnts_out:
            print("  " + elmnt.name)

    @staticmethod
    def get_element_by_name(elements_list, name, return_id_in_list=True):
        '''
        Возвращает элемент модели с указанным name. 
        Если элемент не найден, возвращается None.

        # Вход

        `elements_list`
            Список элементов

        `name`
            Имя элемента
        '''
        for i, elmnt in enumerate(elements_list):
            if elmnt.name == name:
                if return_id_in_list:
                    return i
                else:
                    return elmnt
        return None

#=======================Класс наблюдателя================================
class NRS_Observer_E(object):
    '''
    Класс наблюдателя. Предназначен для отслеживания изменений состояния элементов модели
    '''
    def __init__(self, elmnt, par_list):
        '''
        При инициации экземпляра класса передаем ему элемент за которым он 
        будет наблюдать и список параметров за которыми он будет наблюдать
            Вход:
                elmnt: Element. Элемент за которым будет осуществляться наблюдение \n
                par_list: List. Список параметров за изменением которых будет следить наблдатель
        '''
        self.elmnt=elmnt
        self.set_par(par_list)
        elmnt.observer=self

    def set_par(self, par_list):
        '''
        Устанавливает список параметров за изменением которых будет следить наблдатель
            Вход:
                par_list: List. Список параметров за изменением которых будет следить наблдатель
            Выход:
                NRS_Observer_E. Ссылка на текущий экземпляр наблюдателя
        '''
        self.par_list=par_list
        return self

    def par_dict_init(self):
        '''
        Инициирует список изменений параметров элемента за которым наблюдает обозреватель\n
        Может использоваться в том числе для очищения истории изменений

            Выход:
                NRS_Observer_E. Ссылка на текущий экземпляр наблюдателя
        '''
        self.par_dict={}
        for i in self.par_list:
            self.par_dict[i]=[]
        return self

    def fix(self):
        '''
        Фиксирует текущее состояние параметров элемента за которым наблюдает обозреватель\n       
            Выход:
                NRS_Observer_E. Ссылка на текущий экземпляр наблюдателя
        '''
        for i in self.par_list:
            self.par_dict[i].append(self.elmnt.__dict__[i])
        return self

    def history(self):
        '''
        Возвращает историю изменений параметров элемента за которым наблюдает обозреватель\n       
            Выход:
                Dictionary. Словарь списков (историй изменений)
        '''
        return self.par_dict

        
#=======================Функции расчета расходов================================
def q_out_simple(elmnt):
    '''
    Функция расчета расхода на элементе\n
    Простая - расход на выходе элемента равен расходу на входе
        Выход:
            float. Расход л/с
    '''
    return elmnt.q

def q_out_nozzle(elmnt):
    '''
    Функция расчета расхода на элементе\n
    Производительность стволов - расход на выходе элемента равен проводимости насадка умноженной на корень из напора на входе.
        Выход:
            float. Расход л/с
    '''
    return elmnt.p*pow(elmnt.H_in, 0.5)


#=======================Класс элемента НРС (узла)===============================
class Element(object):
    '''
    Класс элемента НРС.
    '''

    def __init__(self, name, e_type, q=3.7, s=0, H_in=0, h=0, H_add=0, z=0, p=1, n=1, l=0, ri=1, ro=1,
                 q_out = q_out_simple):
        '''
        # Аргументы
            `name`: String. Имя элемента

            `e_type`: тип элемента: 0 - подача (например, насос), 1 - связи (рукавные линии и оборудование), 2 - расход (например, стволы)

            `q`=3.7: стартовый расход через элемент, л/с

            `s`=0: гидравлическое сопротивление элемента

            `H_in`=40: Напор на входе в элемент, м

            `h`=0: стартовые потери напора на элементе, м

            `H_add`=0: дополнительный напор на элементе, м. Например, напор на насосе.

            `z`=0: перепад высот на элементе, м

            `p`=1: проводимость элемента. Для большинства элементов = 1, для расходов должен браться в соответствии с табличными значениями

            `n`=1: количество единиц элемента. Например, количество рукавов в рукавной линии

            `l`=0: длина единицы элемента. По умолчанию предполагается, что все элементы - точечные, т.е не имеют длины

            `ri`=1, `ro`=1: количество входов и выходов соответственно

            `q_out` = q_out_simple: функция расчета расхода на выходе из элемента
        '''
        self.elements_next=[]
        self.elements_previous=[]

        self.type = e_type
        self.name = name
        # print("Новый элемент НРС: " + self.name)

        self.q =q
        self.s=s
        self.H_in=H_in
        self.h=h
        self.z=z
        self.p=p
        self.n=n
        self.q_out=q_out
        self.H_add=H_add
        self.observer=None
        self.l = l
        self.ri = ri
        self.ro = ro
        # self.h=0

    def append(self, elmnt):
        '''
        Подключает элемент к выходу текущего
            Вход:
                elmnt=Element: Элемент который подключается к текущему
            Выход:
                ссылка на текущий элемент
        '''
        # если имеется возможность подключения дополнительного элемента у текущего элемента
        if self.ro>len(self.elements_next):
            # Если у переданного элемента имеется возможность подключения дополнительного эл-та:
            if elmnt.ri>len(elmnt.elements_previous):
                self.elements_next.append(elmnt)
                elmnt.elements_previous.append(self)
            else:
                logger.debug(f'У элемента {elmnt.name} нет дополнительных входов для подключения {self.name}')
        else:
            logger.debug(f'У элемента {self.name} нет дополнительных выходов для подключения {elmnt.name}')
        return elmnt

    def addToModel(self, model):
        '''
        Включает элемент в модель
            Вход:
                model=Model: ссылка на модель в которую следует включить текущий элемент
            Выход:
                ссылка на текущий элемент
        '''
        model.appendElement(self)
        return self

    def fixState(self):
        '''
        Фиксирует состояние параметров элемента
            Выход:
                ссылка на текущий элемент
        '''
        if self.observer:
            self.observer.fix()
        return self

    def history(self):
        '''
        Возвращает историю изменений элемента
            Выход:
                список изменений (при наличии подключенного наблюдателя)
        '''
        if self.observer:
            return self.observer.history()
        else:
            return []

    def observerInit(self):
        '''
        Инициация наблюдателя (при наличии). Имеющаяся история изменений будет удалена.
        '''
        if self.observer:
            return self.observer.par_dict_init()
        return self

    def drop_links(self, linked_elements=False, current_element=True):
        '''
        Очистка связей элемента
        '''
        if linked_elements:
            for elmnt_next in self.elements_next:
                # eid = NRS_Revision.get_element_by_name(elmnt_next.elements_previous, self.name)
                # del elmnt_next.elements_previous[eid]
                if self in elmnt_next.elements_previous:
                    elmnt_next.elements_previous.remove(self)
            for elmnt_prev in self.elements_previous:
                # eid = NRS_Revision.get_element_by_name(elmnt_prev.elements_next, self.name)
                # del elmnt_prev.elements_next[eid]
                if self in elmnt_prev.elements_next:
                    elmnt_prev.elements_next.remove(self)

        if current_element:
            self.elements_next=[]
            self.elements_previous=[]

    def set_ri(self, new_val):
        '''
        Установка количества входных патрубков.
        Если в данный момент к элементу подключено больше элементов на вход, чем новое ri, то лишние отбрасываются.
        '''
        self.ri = new_val
        if self.ri<len(self.elements_previous):
            num_to_drop=len(self.elements_previous)-self.ri
            for _ in range(num_to_drop):
                pe = self.elements_previous.pop(0)
                pe.elements_next.remove(self)
                # self.delElement(pe)

    def set_ro(self, new_val):
        '''
        Установка количества выходных патрубков.
        Если в данный момент к элементу подключено больше элементов на выход, чем новое ro, то лишние отбрасываются.
        '''
        self.ro = new_val
        if self.ro<len(self.elements_next):
            num_to_drop=len(self.elements_next)-self.ro
            for _ in range(num_to_drop):
                ne = self.elements_next.pop(0)
                ne.elements_previous.remove(self)
                # self.delElement(ne)


    # Прямая установка значений
    def get_h(self):
        '''
        Установка потери напора
            Выход:
                float: текущее значение потери напора для данного элемента. 
                Равно S*n*q^2
        '''
        self.h = self.s * self.n * self.q**2 
        return self.h

    def get_H_out(self):
        '''
        Установка напора на выходе из элемента.
            Выход:
                float: текущее значение напора на выходе из элемента.
                Равно H_in + h_add - h - z
        '''
        self.H_out = self.H_in + self.H_add - self.get_h() - self.z
        return self.H_out

    def get_q_out(self):
        '''
        Возвращает расход на выходе из элемента
            Выход:
                float - расход на выходе из элемента. Рассчитывается в соответствии с указанной функцией q_out()
        '''
        return self.q_out(self)

    def set_H_add(self, H_add):
        '''
        Устанавливает дополнительный напор для текущего элемента, 
        а также далее запускает рекурсивный перерасчет напоров 
        для всех следующих после текущего элементов
            Вход:
                H_add=float: дополнительный напор, м
        '''
        self.H_add = H_add
        # for elmnt in self.elements_next:
        #     elmnt.set_H_in(self.get_H_out())        

    def get_L(self):
        '''
        Возвращает длину элемента
        '''
        self.L = self.n * self.l
        return self.L

    # Рекурсивная установка значений
    def set_H_in(self, H_in):
        '''
        Устанавливает напор на входе для текущего элемента, 
        а так же далее запускает рекурсивный перерасчет напоров 
        для всех следующих после текущего элементов
            Вход:
                H_in=float: напор на входе в элемент, м
        '''
        self.H_in = H_in
        for elmnt in self.elements_next:
            # print(elmnt.name, self.get_H_out())
            elmnt.set_H_in(self.get_H_out())

    def set_q_zero(self):
        '''
        Устанавливает нулевой расход для текущего элемента, 
        а так же далее запускает рекурсивный перерасчет расходов 
        для всех предыдущих относительно текущего элементов. \n
        Используется для очищения значений расходов при расчете.
        '''
        self.q=0
        for elmnt in self.elements_previous:
            elmnt.set_q_zero()

    def set_q(self, q):
        '''
        Устанавливает расход для текущего элемента,
        а так же далее запускает рекурсивный перерасчет расходов 
        для всех предыдущих относительно текущего элементов.\n
        Для каждого элемента происходит суммирование в том случае,
        если элемент является водосборником \n
        Если к элементу подключено несколько других элементов на вход
        Расход к ним разделяется поровну (в данной реализации).
        '''
        self.q+=q
        for elmnt in self.elements_previous:
            elmnt.set_q(q/len(self.elements_previous))
            # Тут нужно разобраться
            # if elmnt.type == 0:
            #     elmnt.H_add = self.h + self.H_in

class NRS_Model(object):
    '''
    Класс модели НРС
    '''
    # 'name'
    # elmnts=[]                 # Коллекция всх элементов модели
    # elmnts_in=[]              # Коллекция элементов с входящим потоком (для которых выполняется расчет) - для промежуточных не выполняется
    # elmnts_out=[]             # Коллекция элементов с выходящим потоком (для стволов)

    def __init__(self, name):
        '''
        Инициация класса
            Вход:
                name=string: имя модели
        '''
        self.name = name
        self.elmnts=[]
        self.elmnts_in=[]
        self.elmnts_out=[]
        self.counter=0
        print("Новая модель: " + self.name)

    def appendElement(self, elmnt):
        '''
        Добавляет элемент в модель
            Вход:
                elmnt=Element: Элемент для добавления в модель НРС
            Выход:
                NRS_Model: ссылка на текущую модель
        '''
        self.counter+=1
        if elmnt.name=='':
            elmnt.name=str(self.counter)
        logger.info("Новый элемент НРС: " + elmnt.name)
        
        # добавление в основной список
        self.elmnts.append(elmnt)
        # # Добавление в дополнительные списки
        # if elmnt.type==0:
        #     self.elmnts_in.append(elmnt)
        # elif elmnt.type==2:
        #     self.elmnts_out.append(elmnt)

        return self

    def addElements(self, elmnts, interpretate=False):
        '''
        Добавляет элементы в модель
            Вход:
                elmnts=List(Element): Список элементов для добавления в модель НРС
                interpretate=False: Если равно True, происходит автоматическая интерпретация 
                (распределение по спискам входящих и выходящих элементов)
                элементов модели
            Выход:
                NRS_Model: ссылка на текущую модель
        '''
        for elmnt in elmnts:
            if not elmnt in self.elmnts:
                self.appendElement(elmnt)
        if interpretate:
            self.interpretate()

        return self

    def delElement(self, elmnt:Element):
        '''
        Удаляем элемент как объект
        '''
        # elmnts_next = elmnt.elements_next
        # elements_previous = elmnt.elements_previous
        # elmnt.drop_links(True)
        # for en in elmnts_next:
        #     self.fire_dead_elements_try(en)
        # for ep in elements_previous:
        #     self.fire_dead_elements_try(ep)
        elmnt.drop_links(linked_elements=True, current_element=False)
        for en in elmnt.elements_next:
            self.fire_dead_elements_try(en)
        for ep in elmnt.elements_previous:
            self.fire_dead_elements_try(ep)
        elmnt.drop_links(linked_elements=False, current_element=True)


        if elmnt in self.elmnts:
            self.elmnts.remove(elmnt)
        if elmnt in self.elmnts_in:
            self.elmnts_in.remove(elmnt)
        if elmnt in self.elmnts_out:
            self.elmnts_out.remove(elmnt)


    def fire_dead_elements_try(self, elmnt: Element):
        '''
        Рекурсивная попытка удалить мертвые элементы из модели
        '''
        # print('Проверка элемента:', elmnt.name)
        if elmnt.type==0 and len(elmnt.elements_next)==0:
            elmnt.drop_links(linked_elements=True, current_element=False)
            for ep in elmnt.elements_previous:
                self.fire_dead_elements_try(ep)
            self.delElement(elmnt)
        elif elmnt.type==1 and (len(elmnt.elements_next)==0 or len(elmnt.elements_previous)==0):
            elmnt.drop_links(linked_elements=True, current_element=False)
            for en in elmnt.elements_next:
                self.fire_dead_elements_try(en)
            for ep in elmnt.elements_previous:
                self.fire_dead_elements_try(ep)
            self.delElement(elmnt)
        elif elmnt.type==2 and len(elmnt.elements_previous)==0:
            elmnt.drop_links(linked_elements=True, current_element=False)
            for en in elmnt.elements_next:
                self.fire_dead_elements_try(en)
            self.delElement(elmnt)
        return self

    def getElement(self, name):
        '''
        Возвращает элемент модели с указанным name. 
        Если элемент не найден, возвращается None.

        # Вход

        `name`
            Имя элемента
        '''
        for elmnt in self.elmnts:
            if name == elmnt.name:
                return elmnt
        return None


    def interpretate(self):
        '''
        Интерпретация 
        (распределеине по спискам входящих и выходящих элементов)
        элементов модели
            Выход:
                NRS_Model: ссылка на текущую модель
        '''
        for elmnt in self.elmnts:
            if elmnt.type==0 and not elmnt in self.elmnts_in:
                self.elmnts_in.append(elmnt)
            elif elmnt.type==2 and not elmnt in self.elmnts_out:
                self.elmnts_out.append(elmnt)
        # logger.warning("Функция `interpretate` устарела и в будущем будет удалена. Ее использование настоятельно не рекомендуется!")
        return self

    def clear(self):
        '''
        Очистка списков элементов
        '''
        self.elmnts=[]
        self.elmnts_in=[]
        self.elmnts_out=[]
        self.counter=0
        return self

    def addElementsIn(self, elmnts):
        '''
        Добавляет элементы в список элементов-источников (насосы и прочее)
            Вход:
                elmnts=List(Element): Список элементов для добавления в список элементов-источников 
            Выход:
                NRS_Model: ссылка на текущую модель
        '''
        self.elmnts_in=elmnts
        return self

    def addElementsOut(self, elmnts):
        '''
        Добавляет элементы в список элементов-расхода (стволы и прочее)
            Вход:
                elmnts=List(Element): Список элементов для добавления в список элементов-расхода 
            Выход:
                NRS_Model: ссылка на текущую модель
        '''
        self.elmnts_out=elmnts
        return self

    def build(self, elmnt, interpretate=False):
        '''
        Построение модели из единственного элемента
            Вход:
                elmnt=Element: Стартовый элемент от которого будет происходить построение модели\n
                interpretate=False: Если равно True, происходит автоматическая интерпретация 
                (распределеине по спискам входящих и выходящих элементов)
                элементов модели
        '''
        self._elementAdd(elmnt)
        
        if interpretate:
            self.interpretate()

        return self

    def _elementAdd(self, elmnt):
        '''
        Рекурсивное добавление элементов в модель
            Вход:
                elmnt=Element: элемент который следует добавить модель. 
                Далее _elementAdd будет вызвана для всех подключенных к нему элементов
        '''
        if not elmnt in self.elmnts:
            self.appendElement(elmnt)
            for linked in elmnt.elements_next:
                self._elementAdd(linked)
            for linked in elmnt.elements_previous:
                self._elementAdd(linked)

    def observersInit(self):
        '''
        Инициация всех обозревателей модели
            Выход:
                NRS_Model: ссылка на текущую модель
        '''
        for elmnt in self.elmnts:
            elmnt.observerInit()
        return self

    def calc(self, iters=1, callback=None, accuracy=0, fixStates=True):
        '''
        Рассчитывает модель
            Вход:
                iters - количество циклов расчета, ед. По умолчанию iters=1 \n
                callback - функция вызываемая по окончании каждой итерации. По умолчанию callback=None \n
                accuracy=0:float - точность расчета НРС. Если точность не равна 0, то модель будет рассчитываться до тех пор, пока не будет достигнута указанная точность. \n
                fixStates=True:Bool - фиксировать ли состояния модели при расчете
            Выход:
                NRS_Model - ссылка на текущий экземпляр модели\n
                int - количество итераций потребовавшихся для достижения необходимой точности расчета (при accuracy>0)
        '''
        # Q=[10000, 1000, self.summaryQ()]
        Q=[100000, 10000, 1000]
        # print(Q)
        if accuracy==0:
            # if iters>=3:
                # Q=[0,0,0]
            for i in range(iters):
                for elmnt in self.elmnts_in:
                    elmnt.set_H_in(elmnt.H_in)
                    # elmnt.set_H_in(elmnt.H_add + elmnt.H_in)  elmnt.H_add = self.h + self.H_in
                for elmnt in self.elmnts_out:
                    elmnt.set_q_zero()
                for elmnt in self.elmnts_out:
                    elmnt.set_q(elmnt.get_q_out())
                if fixStates:
                    self.fixState()
                    # for elmnt in self.elmnts:
                    #     elmnt.fixState()
                if callback:
                    callback(self)

                # if iters>=3:
                Q[0]=Q[1]
                Q[1]=Q[2]
                Q[2]=self.summaryQ()

                QD_1=abs(Q[1]-Q[0])
                QD_2=abs(Q[2]-Q[1])

                # if QD_1<QD_2:
                #     print("Расчет НРС не возможен")

        if accuracy>0:
            i=0
            # print('до', Q)
            # while abs(Q[2]-Q[1])>accuracy:      # and not Q[2]==Q[1]:
            while abs(Q[2]-Q[1])>accuracy and Q[2]!=Q[1]:
                # print(i)
                # print('0', Q)
                for elmnt in self.elmnts_in:
                    elmnt.set_H_in(elmnt.H_in)      
                    # elmnt.set_H_in(elmnt.H_add + elmnt.H_in)
                for elmnt in self.elmnts_out:
                    elmnt.set_q_zero()
                for elmnt in self.elmnts_out:
                    elmnt.set_q(elmnt.get_q_out())
                if fixStates:
                    self.fixState()
                    # for elmnt in self.elmnts:
                    #     elmnt.fixState()
                if callback:
                    callback(self)

                # if iters>=3:
                Q[0]=Q[1]
                Q[1]=Q[2]
                Q[2]=self.summaryQ()
                # print('1', Q)
                QD_1=abs(Q[1]-Q[0])
                QD_2=abs(Q[2]-Q[1])
                if QD_1<QD_2:
                    # logger.debug("Расчет НРС не возможен")
                    # print('Невязки', Q, QD_1, QD_2)
                    raise ValueError("НРС с заданными параметрами не работоспособна")

                i+=1

            # QD_2 - QD_1 - невязка модели
            QD_1=abs(Q[1]-Q[0])
            QD_2=abs(Q[2]-Q[1])
            return self, {'iters':i, 'QD2':QD_2, 'correct':True}

        return self, QD_2 #- QD_1

    def summaryQ(self):
        '''
        Возвращает общий расход модели
        
        # Выход
        
        `float`: суммарный расход модели, л/с
        '''
        return sum([elmnt.get_q_out() for elmnt in self.elmnts_out])
    
    def drop_q(self):
        '''
        Сбрасывает все текущие расходы элементов. 
        Предназначена для возможности повторного расчета модели.
        '''
        for elmnt in self.elmnts:
            elmnt.q = 0

    def fixState(self):
        '''
        Фиксирует состояние параметров элементов модели
        '''
        for elmnt in self.elmnts:
            elmnt.fixState()


class NRS_Data(object):
    '''
    Модуль табличных данных для расчета НРС
    '''
    s = {
        "Прорезиненный напорный рукав 38 мм (20м)": 0.34,
        "Прорезиненный напорный рукав 51 мм (20м)": 0.13,
        "Прорезиненный напорный рукав 66 мм (20м)": 0.034,
        "Прорезиненный напорный рукав 77 мм (20м)": 0.015,
        "Прорезиненный напорный рукав 89 мм (20м)": 0.0035,
        "Прорезиненный напорный рукав 110 мм (20м)": 0.002,
        "Прорезиненный напорный рукав 150 мм (20м)": 0.00046,
        "Прорезиненный напорный рукав 200 мм (100м)": 0.00006,
        "Прорезиненный напорный рукав 225 мм (100м)": 0.000184,
        "Прорезиненный напорный рукав 250 мм (100м)": 0.0000136,
        "Прорезиненный напорный рукав 300 мм (100м)": 0.0000056,
        "Непрорезиненный напорный рукав диаметром 51мм (20м)": 0.03,
        "Непрорезиненный напорный рукав диаметром 66мм (20м)": 0.077,
        "Непрорезиненный напорный рукав диаметром 77мм (20м)": 0.24,
        "Напорный рукав с двухсторонним покрытием диаметром 38мм (20м)": 0.51
    }

    ss = {
        "38": s["Прорезиненный напорный рукав 38 мм (20м)"],
        "51": s["Прорезиненный напорный рукав 51 мм (20м)"],
        "66": s["Прорезиненный напорный рукав 66 мм (20м)"],
        "77": s["Прорезиненный напорный рукав 77 мм (20м)"],
        "89": s["Прорезиненный напорный рукав 89 мм (20м)"],
        "110": s["Прорезиненный напорный рукав 110 мм (20м)"],
        "150": s["Прорезиненный напорный рукав 150 мм (20м)"],
        "200": s["Прорезиненный напорный рукав 200 мм (100м)"],
        "225": s["Прорезиненный напорный рукав 225 мм (100м)"],
        "250": s["Прорезиненный напорный рукав 250 мм (100м)"],
        "300": s["Прорезиненный напорный рукав 300 мм (100м)"],
        "38дв": s["Напорный рукав с двухсторонним покрытием диаметром 38мм (20м)"],
        "51нп": s["Непрорезиненный напорный рукав диаметром 51мм (20м)"],
        "66нп": s["Непрорезиненный напорный рукав диаметром 66мм (20м)"],
        "77нп": s["Непрорезиненный напорный рукав диаметром 77мм (20м)"],
    }

    aa = {
        "38": s["Прорезиненный напорный рукав 38 мм (20м)"]/20,
        "51": s["Прорезиненный напорный рукав 51 мм (20м)"]/20,
        "66": s["Прорезиненный напорный рукав 66 мм (20м)"]/20,
        "77": s["Прорезиненный напорный рукав 77 мм (20м)"]/20,
        "89": s["Прорезиненный напорный рукав 89 мм (20м)"]/20,
        "110": s["Прорезиненный напорный рукав 110 мм (20м)"]/20,
        "150": s["Прорезиненный напорный рукав 150 мм (20м)"]/20,
        "200": s["Прорезиненный напорный рукав 200 мм (100м)"]/100,
        "225": s["Прорезиненный напорный рукав 225 мм (100м)"]/100,
        "250": s["Прорезиненный напорный рукав 250 мм (100м)"]/100,
        "300": s["Прорезиненный напорный рукав 300 мм (100м)"]/100,
        "38дв": s["Напорный рукав с двухсторонним покрытием диаметром 38мм (20м)"]/20,
        "51нп": s["Непрорезиненный напорный рукав диаметром 51мм (20м)"]/20,
        "66нп": s["Непрорезиненный напорный рукав диаметром 66мм (20м)"]/20,
        "77нп": s["Непрорезиненный напорный рукав диаметром 77мм (20м)"]/20,
    }


# #%% ===================Прямые тесты=========================================
# NRS_Data.s['Прорезиненный напорный рукав 51 мм']
# print(NRS_Data.ss.keys())
# print(NRS_Data.ss)


# model = NRS_Model("test model")

# pump = Element('Насос', 0, H_add=40)  #.addToModel(model)
# hoseM1 = Element('МРЛ', 1, s=0.015, n=3)  #.addToModel(model)
# splitter = Element('Разветвление', 1)  #.addToModel(model)
# hoseW1 = Element('РРЛ 1', 1, s=0.13, n=1)  #.addToModel(model)
# hoseW2 = Element('РРЛ 2', 1, s=0.13, n=3)  #.addToModel(model)
# nozzle1 = Element('Ствол 1', 2, p=1.17, q_out = q_out_nozzle)  #.addToModel(model)
# nozzle2 = Element('Ствол 2', 2, p=1.17, q_out = q_out_nozzle)  #.addToModel(model)

# pump.append(hoseM1).append(splitter)
# splitter.append(hoseW1).append(nozzle1)
# splitter.append(hoseW2).append(nozzle2)

# NRS_Observer_E(hoseM1, ['q', 'H_in'])
# NRS_Observer_E(nozzle1, ['q', 'H_in'])
# NRS_Observer_E(nozzle2,['q', 'H_in'])

# model.build(pump, interpretate=True)
# NRS_Revision.print_model_elements(model)

# # Предварительный прогон
# model.observersInit()
# model.calc(iters=10)
# print(model.summaryQ())

# print("="*10)
# pump.set_H_add(80)
# model.observersInit()
# _, iters_count = model.calc(accuracy=0.1)
# print(model.summaryQ())
# print("Потребовалось итераций: {}".format(iters_count))


##%%
# # model.interpretate()
# # model = NRS_Model("test model")
# # model.addElements([pump,hoseM1,splitter,hoseW1,hoseW2,nozzle1,nozzle2], interpretate=True)
# # model.addElementsIn([pump])
# # model.addElementsOut([nozzle1,nozzle2])



# iteration=0

# #%%
# model.calc()
# print(str(iteration) + ", q=" + str(model.summaryQ()))
# iteration+=1

# #%%
# print(nozzle1.history()['q'])
# print(nozzle1.history()['H_in'])

# #%%
# pump.H_in=40

# #%%
# NRS_Revision.print_model_elements(model)
# # print("all:")
# # for elmnt in model.elmnts:
# #     print("  " + elmnt.name)
# # print("in:")
# # for elmnt in model.elmnts_in:
# #     print("  " + elmnt.name)
# # print("out:")
# # for elmnt in model.elmnts_out:
# #     print("  " + elmnt.name)





# #%% Без модели
# pump = Element('Насос', 0)
# hoseM1 = Element('МРЛ', 1, s=0.015, n=3)
# splitter = Element('Разветвление', 1)
# hoseW1 = Element('РРЛ 1', 1, s=0.13, n=1)
# hoseW2 = Element('РРЛ 2', 1, s=0.13, n=3)
# nozzle1 = Element('Ствол 1', 2, p=1.17, q_out = q_out_nozzle)
# nozzle2 = Element('Ствол 2', 2, p=1.17, q_out = q_out_nozzle)

# pump.append(hoseM1).append(splitter)
# splitter.append(hoseW1).append(nozzle1)
# splitter.append(hoseW2).append(nozzle2)


# watcher_hoseM1 = NRS_Observer_E(hoseM1, ['q','h', 'H_in']).par_dict_init()
# watcher_nozzle1 = NRS_Observer_E(nozzle1, ['q', 'H_in']).par_dict_init()
# watcher_nozzle2 = NRS_Observer_E(nozzle2,['q', 'H_in']).par_dict_init()

# # %%
# # print(hoseM1.__dict__)
# # print(hoseM1.observer.fix())
# # print(hoseM1.observer.__dict__)



# #%%
# iteration=0
# # watcher_Splitter.par_dict_init()
# watcher_hoseM1.par_dict_init()
# watcher_nozzle1.par_dict_init()
# watcher_nozzle2.par_dict_init()


# #%%
# H=80
# print(str(iteration) + "="*10)
# iteration+=1

# # Расчет напоров (прямой)
# pump.set_H_in(H)

# # print(nozzle1.H_in, nozzle1.get_q_out())
# # print(nozzle2.H_in, nozzle2.get_q_out())

# # Расчет расходов (обратный)
# nozzle1.set_q_zero()
# nozzle2.set_q_zero()
# nozzle1.set_q(nozzle1.get_q_out())
# nozzle2.set_q(nozzle2.get_q_out())

# # фиксируем состояние элемента
# hoseM1.fixState()
# nozzle1.fixState()
# nozzle2.fixState()

# #%%
# print(hoseM1.observer.history()['q'])




# # %%
# a=[1,2,3,4,5]
# print(sum([q for q in a]))
# # %%
# print(not 7 in [1,2,3,4,7])