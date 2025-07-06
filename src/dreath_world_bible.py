from typing import Dict, List, Optional, Union
from pydantic import BaseModel

# ========== 基础模型 ==========
class GeoCoordinates(BaseModel):
    """地理坐标系统"""
    lat: float
    lon: float
    elevation: Optional[float] = None  # 海拔高度

class TemporalRange(BaseModel):
    """时间范围"""
    start_year: int
    end_year: Optional[int] = None  # 未结束则为空

# ========== 世界基础与宇宙观 ==========
class PlanetaryProperties(BaseModel):
    """星球特性"""
    diameter_km: float
    surface_gravity: float
    atmospheric_composition: Dict[str, float]  # 气体成分及比例
    magnetic_field: bool
    rotation_period_hours: float
    orbital_period_days: float
    seasons: List[str]  # 季节名称
    moons: List[str]  # 卫星名称

class Continent(BaseModel):
    """大陆定义"""
    name: str
    coordinates: List[GeoCoordinates]  # 边界坐标

class ClimateZone(BaseModel):
    """气候带"""
    name: str
    temperature_range: str  # 温度范围
    precipitation: str  # 降水类型
    biomes: List[str]  # 主要生物群系

class CalendarSystem(BaseModel):
    """历法系统"""
    year_name: str
    month_names: List[str]
    week_days: List[str]
    seasons: List[str]
    leap_year_rule: str

class WorldFoundation(BaseModel):
    """世界基础与宇宙观"""
    planetary_properties: PlanetaryProperties
    continents: List[Continent]
    oceans: List[str]
    climate_zones: List[ClimateZone]
    geological_activity: List[str]  # 地质活动类型
    time_units: Dict[str, float]  # 时间单位定义
    calendar: CalendarSystem
    special_phenomena: List[str]  # 特殊现象

# ========== 世界与地理 ==========
class TerrainFeature(BaseModel):
    """地形特征"""
    type: str  # 山脉/平原/森林等
    name: str
    coordinates: List[GeoCoordinates]

class ResourceDistribution(BaseModel):
    """资源分布"""
    resource_type: str
    locations: List[str]
    abundance: str  # 丰富程度

class Landmark(BaseModel):
    """地标"""
    name: str
    type: str  # 自然/人造
    significance: str
    coordinates: GeoCoordinates

class Region(BaseModel):
    """大陆区域"""
    name: str
    boundaries: List[GeoCoordinates]
    terrain_features: List[TerrainFeature]
    climate: str
    resources: List[ResourceDistribution]
    landmarks: List[Landmark]

class SettlementHistory(BaseModel):
    """聚落历史"""
    founding_year: int
    major_events: List[str]

class City(BaseModel):
    """城市定义"""
    name: str
    location: GeoCoordinates
    districts: Dict[str, str]  # 分区及功能
    population: int
    demographics: Dict[str, float]  # 种族比例
    economy: List[str]  # 经济支柱
    culture: str
    landmarks: List[str]
    history: SettlementHistory

class Nation(BaseModel):
    """国家定义"""
    name: str
    territory: List[GeoCoordinates]
    capital: str
    major_cities: List[str]
    political_influence: str
    history: str

class WildernessArea(BaseModel):
    """荒野与秘境"""
    name: str
    description: str
    location: GeoCoordinates
    notes: str  # 特殊备注

class WorldGeography(BaseModel):
    """世界地理总览"""
    regions: List[Region]
    nations: List[Nation]
    cities: List[City]
    wilderness_areas: List[WildernessArea]

# ========== 生命与种族 ==========
class Physiology(BaseModel):
    """生理特征"""
    lifespan: int
    appearance: str
    spirit_vessel_organ: str  # 灵蕴器官位置
    height_range: str
    special_features: List[str]

class Race(BaseModel):
    """智慧种族"""
    name: str
    physiology: Physiology
    origin: str
    social_structure: str
    culture: str
    settlements: List[str]  # 主要聚居地
    subspecies: List[str]  # 亚种分支
    relations: Dict[str, str]  # 与其他种族关系

class Creature(BaseModel):
    """生物基础"""
    name: str
    habitat: str
    behavior: str
    special_abilities: List[str]

class SpiritBeast(Creature):
    """灵兽"""
    spirit_power_level: str  # 灵力等级
    spirit_affinity: str  # 灵力亲和类型

class Ecosystem(BaseModel):
    """生态系统"""
    name: str
    food_chain: List[List[str]]  # 食物链层级
    keystone_species: List[str]  # 关键物种

class LifeForms(BaseModel):
    """生命体系"""
    sapient_races: List[Race]
    non_spirit_creatures: List[Creature]  # 无灵生物
    spirit_infused_creatures: List[Creature]  # 灵力生物
    spirit_beasts: List[SpiritBeast]
    special_creatures: List[Creature]  # 特殊生物
    ecosystems: List[Ecosystem]

# ========== 灵力与灵术体系 ==========
class SpiritTheory(BaseModel):
    """灵力理论流派"""
    name: str  # 大无垠论/神恩论等
    core_principles: str
    key_proponents: List[str]  # 主要支持者

class SpiritVesselType(BaseModel):
    """灵蕴类型"""
    category: str  # 物质类/强化类/控制类
    description: str
    common_manifestations: List[str]  # 常见表现

class AwakeningRitual(BaseModel):
    """觉醒仪式"""
    requirements: List[str]
    process: str
    success_rate: float
    risks: List[str]

class SpiritRank(BaseModel):
    """灵术等级"""
    name: str  # 藏道/蕴灵/凭风等
    abilities: List[str]
    social_status: str
    approx_percentage: float  # 人口占比

class SpiritApplication(BaseModel):
    """灵术应用"""
    name: str
    type: str  # 日常/战斗/工业等
    description: str
    required_rank: Optional[str] = None

class SpiritSystem(BaseModel):
    """灵力体系总览"""
    core_definition: str
    properties: List[str]
    world_impact: List[str]
    theories: List[SpiritTheory]
    vessel_types: List[SpiritVesselType]
    awakening_ritual: AwakeningRitual
    ranks: List[SpiritRank]
    applications: List[SpiritApplication]
    storage_methods: List[str]  # 灵力存储技术
    spirit_tools: List[str]  # 灵力器具
    professions: List[str]  # 灵职

# ========== 完整世界设定 ==========
class DrearthWorld(BaseModel):
    """Drearth世界完整设定集"""
    foundation: WorldFoundation
    geography: WorldGeography
    life_forms: LifeForms
    spirit_system: SpiritSystem
    # 以下部分数据结构类似，因篇幅限制仅展示核心部分
    # history: WorldHistory
    # society: SocialStructure
    # religion: FaithSystem
    # technology: TechnologicalDevelopment
    # artifacts: ItemsAndBooks

# ===== 使用示例 =====
if __name__ == "__main__":
    # 创建星球特性实例
    planetary_props = PlanetaryProperties(
        diameter_km=12742,
        surface_gravity=9.8,
        atmospheric_composition={"N2": 0.78, "O2": 0.21},
        magnetic_field=True,
        rotation_period_hours=24,
        orbital_period_days=365,
        seasons=["春", "夏", "秋", "冬"],
        moons=["露娜"]
    )
    
    # 创建灵蕴等级实例
    zangdao_rank = SpiritRank(
        name="藏道",
        abilities=["引灵入体", "体能强化"],
        social_status="超越常人的精英",
        approx_percentage=0.1
    )
    
    # 创建种族实例
    human_physiology = Physiology(
        lifespan=80,
        appearance="标准人类特征",
        spirit_vessel_organ="颅内灵核",
        height_range="150-190cm",
        special_features=["适应性强的灵蕴器官"]
    )
    
    # 创建世界基础实例
    world_foundation = WorldFoundation(
        planetary_properties=planetary_props,
        continents=[Continent(name="齐维尔", coordinates=[])],
        oceans=["蔚蓝之海"],
        climate_zones=[ClimateZone(name="温带", temperature_range="-10~30℃", precipitation="均衡", biomes=["森林","草原"])],
        geological_activity=["火山带", "地震带"],
        time_units={"年": 365, "月": 30},
        calendar=CalendarSystem(
            year_name="星历",
            month_names=["初芽","花月","炎夏"]+["..."]*9,
            week_days=["星耀日","月辉日","火曜日","水曜日","木曜日","金曜日","土息日"],
            seasons=["萌春","盛夏","丰秋","静冬"],
            leap_year_rule="每四年一闰"
        ),
        special_phenomena=["灵潮涌动","双月同天"]
    )
    
    # 构建完整世界实例
    drearth = DrearthWorld(
        foundation=world_foundation,
        geography=WorldGeography(regions=[], nations=[], cities=[], wilderness_areas=[]),
        life_forms=LifeForms(
            sapient_races=[
                Race(
                    name="人类",
                    physiology=human_physiology,
                    origin="齐维尔大陆原生种族",
                    social_structure="封建城邦制",
                    culture="重视灵蕴觉醒仪式",
                    settlements=["艾瑟伦王国","自由城邦"],
                    subspecies=["高地人","海岸民"],
                    relations={"精灵": "贸易伙伴", "矮人": "技术合作"}
                )
            ],
            non_spirit_creatures=[],
            spirit_infused_creatures=[],
            spirit_beasts=[],
            special_creatures=[],
            ecosystems=[]
        ),
        spirit_system=SpiritSystem(
            core_definition="维度跌落效应的能量",
            properties=["可存储性","环境交互性","生命亲和性"],
            world_impact=["形成灵脉","影响生态","改变地貌"],
            theories=[
                SpiritTheory(
                    name="大无垠论",
                    core_principles="灵力是宇宙本源能量的溢出",
                    key_proponents=["阿尔伯特·灵思"]
                )
            ],
            vessel_types=[
                SpiritVesselType(
                    category="物质类",
                    description="具现化物质的能力",
                    common_manifestations=["灵火生成","岩土塑形"]
                )
            ],
            awakening_ritual=AwakeningRitual(
                requirements=["年满16岁","灵力亲和度>5"],
                process="七日灵泉浸泡仪式",
                success_rate=0.65,
                risks=["灵脉灼伤","精神崩溃"]
            ),
            ranks=[zangdao_rank],
            applications=[
                SpiritApplication(
                    name="灵光术",
                    type="日常",
                    description="基础照明灵术",
                    required_rank="藏道"
                )
            ],
            storage_methods=["灵石","灵液容器"],
            spirit_tools=["灵光石","灵温玉"],
            professions=["灵匠","灵术师"]
        )
    )
    
    # 输出JSON表示
    print(drearth.model_dump_json(indent=2))