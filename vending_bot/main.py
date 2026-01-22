import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

TOKEN = "MTQ2Mzc1MTIzODQ5MDI2MzU2Mg.Ghcg3H.7okGxkJUU2mW3oxikpxwp0Kd71QSo5jdBMBt_U"
GUILD_ID = 1463733916740485298
PRODUCTS_FILE = "data/products.json"
USERS_FILE = "data/users.json"
USER_INFO_FILE = "data/user_info.json"
ADMIN_FILE = "data/admin.json"
SETTINGS_FILE = "data/settings.json"

os.makedirs("data", exist_ok=True)

if not os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)

if not os.path.exists(USER_INFO_FILE):
    with open(USER_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)

if not os.path.exists(ADMIN_FILE):
    with open(ADMIN_FILE, 'w', encoding='utf-8') as f:
        json.dump({"admin_id": None}, f)

if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"review_channel_id": None, "buyer_role_id": None}, f)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)
CORS(app)

@app.route('/products', methods=['GET'])
def get_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/products', methods=['POST'])
def save_products():
    products = request.json
    os.makedirs("data", exist_ok=True)
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"✅ 제품 {len(products)}개 저장 완료!")
    return jsonify({"status": "success"})

def run_flask():
    print("🌐 웹 서버 시작: http://localhost:5000")
    print("📁 저장 위치: data/products.json")
    app.run(port=5000, debug=False, use_reloader=False)

def load_products():
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ 제품 로드 실패: {e}")
    return []

def save_products_file(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ 유저 로드 실패: {e}")
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_user_info():
    try:
        if os.path.exists(USER_INFO_FILE):
            with open(USER_INFO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ 유저 정보 로드 실패: {e}")
    return {}

def save_user_info(user_info):
    with open(USER_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_info, f, ensure_ascii=False, indent=2)

def load_admin():
    try:
        if os.path.exists(ADMIN_FILE):
            with open(ADMIN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("admin_id")
    except Exception as e:
        print(f"❌ 관리자 정보 로드 실패: {e}")
    return None

def save_admin(admin_id):
    with open(ADMIN_FILE, 'w', encoding='utf-8') as f:
        json.dump({"admin_id": admin_id}, f, ensure_ascii=False, indent=2)

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
    return {"review_channel_id": None, "buyer_role_id": None}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def get_user_money(user_id):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {"money": 0, "purchases": []}
        save_users(users)
    return users[user_id]["money"]

def add_user_money(user_id, amount):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {"money": 0, "purchases": []}
    users[user_id]["money"] += amount
    save_users(users)
    return users[user_id]["money"]

def subtract_user_money(user_id, amount):
    users = load_users()
    user_id = str(user_id)
    if user_id not in users:
        return False
    if users[user_id]["money"] < amount:
        return False
    users[user_id]["money"] -= amount
    save_users(users)
    return True

def get_star_display(rating):
    return "⭐" * rating

class UserInfoModal(discord.ui.Modal, title="내 정보 등록"):
    name = discord.ui.TextInput(label="이름", placeholder="실명을 입력하세요", required=True, max_length=20)
    account = discord.ui.TextInput(label="계좌번호", placeholder="은행명 계좌번호 (예: 카카오뱅크 1234-5678-9012)", required=True, max_length=50)
    phone = discord.ui.TextInput(label="전화번호", placeholder="010-1234-5678", required=True, max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        user_info = load_user_info()
        user_id = str(interaction.user.id)
        user_info[user_id] = {
            "name": self.name.value, 
            "account": self.account.value, 
            "phone": self.phone.value, 
            "discord_tag": str(interaction.user)
        }
        save_user_info(user_info)
        money = get_user_money(interaction.user.id)
        embed = discord.Embed(title="✅ 정보 등록 완료", color=0x57F287)
        embed.add_field(name="👤 이름", value=self.name.value, inline=True)
        embed.add_field(name="💰 잔액", value=f"{money:,}원", inline=True)
        embed.add_field(name="📞 전화번호", value=self.phone.value, inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ReviewModal(discord.ui.Modal, title="후기 작성"):
    rating = discord.ui.TextInput(
        label="별점 (1-5)",
        placeholder="1부터 5까지 숫자를 입력하세요",
        required=True,
        max_length=1
    )
    review = discord.ui.TextInput(
        label="후기 내용",
        placeholder="구매하신 제품에 대한 후기를 작성해주세요",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    def __init__(self, product_name: str, user_id: int, guild_id: int):
        super().__init__()
        self.product_name = product_name
        self.user_id = user_id
        self.guild_id = guild_id
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rating_num = int(self.rating.value)
            if rating_num < 1 or rating_num > 5:
                await interaction.response.send_message("❌ 별점은 1부터 5 사이의 숫자여야 합니다!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("❌ 별점은 숫자로 입력해주세요!", ephemeral=True)
            return
        
        settings = load_settings()
        review_channel_id = settings.get("review_channel_id")
        
        if not review_channel_id:
            await interaction.response.send_message("❌ 후기 채널이 설정되지 않았습니다. 관리자에게 문의하세요.", ephemeral=True)
            return
        
        try:
            review_channel = bot.get_channel(review_channel_id)
            if not review_channel:
                review_channel = await bot.fetch_channel(review_channel_id)
            
            embed = discord.Embed(
                title="⭐ 새로운 후기",
                description=self.review.value,
                color=0xFEE75C
            )
            embed.add_field(name="📦 제품", value=self.product_name, inline=True)
            embed.add_field(name="⭐ 별점", value=get_star_display(rating_num), inline=True)
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"작성자 ID: {interaction.user.id}")
            embed.timestamp = discord.utils.utcnow()
            
            await review_channel.send(embed=embed)
            
            # 구매자 역할 부여
            buyer_role_id = settings.get("buyer_role_id")
            
            if buyer_role_id:
                try:
                    guild = bot.get_guild(self.guild_id)
                    if not guild:
                        guild = await bot.fetch_guild(self.guild_id)
                    
                    member = guild.get_member(interaction.user.id)
                    if not member:
                        member = await guild.fetch_member(interaction.user.id)
                    
                    role = guild.get_role(buyer_role_id)
                    
                    if role and member and role not in member.roles:
                        await member.add_roles(role)
                        print(f"✅ {member}님에게 구매자 역할 부여 (후기 작성)")
                        await interaction.response.send_message(
                            f"✅ 후기가 성공적으로 등록되었습니다! 감사합니다 😊\n🎭 {role.name} 역할이 부여되었습니다!",
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message("✅ 후기가 성공적으로 등록되었습니다! 감사합니다 😊", ephemeral=True)
                except Exception as e:
                    print(f"❌ 역할 부여 오류: {e}")
                    await interaction.response.send_message("✅ 후기가 성공적으로 등록되었습니다! 감사합니다 😊", ephemeral=True)
            else:
                await interaction.response.send_message("✅ 후기가 성공적으로 등록되었습니다! 감사합니다 😊", ephemeral=True)
                
        except Exception as e:
            print(f"❌ 후기 전송 오류: {e}")
            await interaction.response.send_message(f"❌ 후기 등록 중 오류가 발생했습니다: {e}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"봇 준비 완료 | {bot.user}")
    print("슬래시 명령어 등록 완료")
    print(f"📦 등록된 제품: {len(load_products())}개")

@bot.tree.command(name="잔액", description="내 잔액을 확인합니다", guild=discord.Object(id=GUILD_ID))
async def check_balance(interaction: discord.Interaction):
    money = get_user_money(interaction.user.id)
    embed = discord.Embed(title="💰 내 잔액", description=f"현재 잔액: **{money:,}원**", color=0xFEE75C)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="관리자설정", description="충전 승인을 받을 관리자를 설정합니다", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(관리자="관리자로 설정할 유저를 멘션하세요")
async def set_admin(interaction: discord.Interaction, 관리자: discord.User):
    # 서버 관리자 권한 확인
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 이 명령어는 서버 관리자만 사용할 수 있습니다!", ephemeral=True)
        return
    
    save_admin(관리자.id)
    
    embed = discord.Embed(
        title="✅ 관리자 설정 완료",
        description=f"충전 승인 관리자가 {관리자.mention}님으로 설정되었습니다!",
        color=0x57F287
    )
    embed.add_field(name="👤 관리자", value=f"{관리자.name} ({관리자.id})", inline=False)
    embed.set_footer(text="이제 충전 신청이 이 관리자에게 전송됩니다.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="관리자확인", description="현재 설정된 관리자를 확인합니다", guild=discord.Object(id=GUILD_ID))
async def check_admin(interaction: discord.Interaction):
    admin_id = load_admin()
    
    if not admin_id:
        embed = discord.Embed(
            title="❌ 관리자 미설정",
            description="아직 관리자가 설정되지 않았습니다.\n\n서버 관리자는 `/관리자설정` 명령어로 관리자를 설정할 수 있습니다.",
            color=0xED4245
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        admin_user = await bot.fetch_user(admin_id)
        embed = discord.Embed(
            title="ℹ️ 현재 관리자",
            description=f"충전 승인 관리자: {admin_user.mention}",
            color=0x5865F2
        )
        embed.add_field(name="👤 이름", value=admin_user.name, inline=True)
        embed.add_field(name="🆔 ID", value=admin_id, inline=True)
        embed.set_thumbnail(url=admin_user.display_avatar.url)
    except:
        embed = discord.Embed(
            title="⚠️ 관리자 정보 오류",
            description=f"관리자 ID: {admin_id}\n\n유저를 찾을 수 없습니다. 관리자를 다시 설정해주세요.",
            color=0xFEE75C
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="후기채널설정", description="후기가 게시될 채널을 설정합니다", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(채널="후기 채널을 선택하세요")
async def set_review_channel(interaction: discord.Interaction, 채널: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 이 명령어는 서버 관리자만 사용할 수 있습니다!", ephemeral=True)
        return
    
    settings = load_settings()
    settings["review_channel_id"] = 채널.id
    save_settings(settings)
    
    embed = discord.Embed(
        title="✅ 후기 채널 설정 완료",
        description=f"후기 채널이 {채널.mention}로 설정되었습니다!",
        color=0x57F287
    )
    embed.set_footer(text="이제 구매자들이 작성한 후기가 이 채널에 게시됩니다.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="구매자역할설정", description="구매자에게 부여할 역할을 설정합니다", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(역할="구매자 역할을 선택하세요")
async def set_buyer_role(interaction: discord.Interaction, 역할: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 이 명령어는 서버 관리자만 사용할 수 있습니다!", ephemeral=True)
        return
    
    settings = load_settings()
    settings["buyer_role_id"] = 역할.id
    save_settings(settings)
    
    embed = discord.Embed(
        title="✅ 구매자 역할 설정 완료",
        description=f"구매자 역할이 {역할.mention}로 설정되었습니다!",
        color=0x57F287
    )
    embed.set_footer(text="이제 제품을 구매한 유저에게 자동으로 이 역할이 부여됩니다.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="설정확인", description="현재 봇 설정을 확인합니다", guild=discord.Object(id=GUILD_ID))
async def check_settings(interaction: discord.Interaction):
    settings = load_settings()
    admin_id = load_admin()
    
    embed = discord.Embed(title="⚙️ 봇 설정", color=0x5865F2)
    
    # 관리자 정보
    if admin_id:
        try:
            admin_user = await bot.fetch_user(admin_id)
            embed.add_field(name="👤 관리자", value=f"{admin_user.mention}", inline=False)
        except:
            embed.add_field(name="👤 관리자", value=f"ID: {admin_id} (찾을 수 없음)", inline=False)
    else:
        embed.add_field(name="👤 관리자", value="❌ 미설정", inline=False)
    
    # 후기 채널
    review_channel_id = settings.get("review_channel_id")
    if review_channel_id:
        channel = bot.get_channel(review_channel_id)
        if channel:
            embed.add_field(name="📝 후기 채널", value=f"{channel.mention}", inline=False)
        else:
            embed.add_field(name="📝 후기 채널", value=f"ID: {review_channel_id} (찾을 수 없음)", inline=False)
    else:
        embed.add_field(name="📝 후기 채널", value="❌ 미설정", inline=False)
    
    # 구매자 역할
    buyer_role_id = settings.get("buyer_role_id")
    if buyer_role_id:
        guild = interaction.guild
        role = guild.get_role(buyer_role_id)
        if role:
            embed.add_field(name="🎭 구매자 역할", value=f"{role.mention}", inline=False)
        else:
            embed.add_field(name="🎭 구매자 역할", value=f"ID: {buyer_role_id} (찾을 수 없음)", inline=False)
    else:
        embed.add_field(name="🎭 구매자 역할", value="❌ 미설정", inline=False)
    
    embed.set_footer(text="💡 서버 관리자만 설정을 변경할 수 있습니다.")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="충전", description="충전 계좌 정보를 확인합니다", guild=discord.Object(id=GUILD_ID))
async def charge_info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💳 충전하기", 
        description="**충전 계좌 정보**\n\n🏦 은행: 카카오뱅크\n💳 계좌번호: 1234-5678-9012\n👤 예금주: 민준\n\n**충전 방법:**\n1. 위 계좌로 원하는 금액 입금\n2. `/충전신청 [금액] [이미지]` 명령어로 영수증 제출\n\n💡 입금자명을 디스코드 닉네임으로 해주세요!", 
        color=0x57F287
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="충전신청", description="충전 영수증을 제출합니다", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(금액="충전 금액", 이미지="입금 영수증 이미지")
async def charge_request(interaction: discord.Interaction, 금액: int, 이미지: discord.Attachment):
    # 먼저 응답 지연 처리
    await interaction.response.defer(ephemeral=True)
    
    try:
        if 금액 <= 0:
            await interaction.followup.send("❌ 충전 금액은 0보다 커야 합니다!", ephemeral=True)
            return
        
        user_info_data = load_user_info()
        user_id = str(interaction.user.id)
        
        if user_id not in user_info_data:
            await interaction.followup.send("❌ 먼저 자판기 정보 버튼을 눌러 개인정보를 등록해주세요!", ephemeral=True)
            return
        
        user_info = user_info_data[user_id]
        
        # 관리자 ID 가져오기
        admin_id = load_admin()
        
        if not admin_id:
            await interaction.followup.send(
                "❌ 관리자가 설정되지 않았습니다.\n\n서버 관리자에게 `/관리자설정` 명령어로 관리자를 설정하도록 요청하세요.",
                ephemeral=True
            )
            return
        
        # 서버 주인에게 DM 보내기
        try:
            admin_user = await bot.fetch_user(admin_id)
        except Exception as e:
            print(f"❌ 관리자 조회 실패: {e}")
            await interaction.followup.send(
                f"❌ 관리자를 찾을 수 없습니다. (ID: {admin_id})\n\n서버 관리자에게 `/관리자설정` 명령어로 관리자를 다시 설정하도록 요청하세요.",
                ephemeral=True
            )
            return
        
        # 이미지 URL 확인
        image_url = 이미지.url
        print(f"📸 이미지 URL: {image_url}")
        
        embed = discord.Embed(title="💳 충전 신청", color=0xFEE75C)
        embed.add_field(name="👤 신청자", value=f"{interaction.user.mention} ({interaction.user.name}#{interaction.user.discriminator})", inline=False)
        embed.add_field(name="💰 금액", value=f"**{금액:,}원**", inline=True)
        embed.add_field(name="🏷️ 이름", value=user_info['name'], inline=True)
        embed.add_field(name="💳 계좌", value=user_info['account'], inline=False)
        embed.add_field(name="📞 전화번호", value=user_info['phone'], inline=True)
        embed.set_image(url=image_url)
        embed.set_footer(text=f"사용자 ID: {interaction.user.id}")
        embed.timestamp = discord.utils.utcnow()
        
        # 버튼 뷰 생성
        view = discord.ui.View(timeout=None)
        
        # 승인 버튼
        approve_btn = discord.ui.Button(
            label="승인", 
            style=discord.ButtonStyle.success, 
            emoji="✅",
            custom_id=f"approve_{interaction.user.id}_{금액}"
        )
        
        # 거절 버튼
        reject_btn = discord.ui.Button(
            label="거절", 
            style=discord.ButtonStyle.danger, 
            emoji="❌",
            custom_id=f"reject_{interaction.user.id}_{금액}"
        )
        
        async def approve_callback(btn_interaction: discord.Interaction):
            try:
                # 버튼 비활성화
                for item in view.children:
                    item.disabled = True
                
                new_balance = add_user_money(interaction.user.id, 금액)
                
                # 관리자에게 메시지
                await btn_interaction.response.edit_message(
                    content=f"✅ {interaction.user.mention}님의 {금액:,}원 충전을 승인했습니다!\n새 잔액: {new_balance:,}원",
                    embed=embed,
                    view=view
                )
                
                # 유저에게 DM
                try:
                    user_embed = discord.Embed(
                        title="✅ 충전 완료",
                        description=f"**{금액:,}원**이 충전되었습니다!",
                        color=0x57F287
                    )
                    user_embed.add_field(name="💰 현재 잔액", value=f"**{new_balance:,}원**", inline=False)
                    await interaction.user.send(embed=user_embed)
                except Exception as e:
                    print(f"❌ 유저 DM 전송 실패: {e}")
            except Exception as e:
                print(f"❌ 승인 처리 오류: {e}")
                await btn_interaction.response.send_message(f"❌ 오류 발생: {e}", ephemeral=True)
        
        async def reject_callback(btn_interaction: discord.Interaction):
            try:
                # 버튼 비활성화
                for item in view.children:
                    item.disabled = True
                
                # 관리자에게 메시지
                await btn_interaction.response.edit_message(
                    content=f"❌ {interaction.user.mention}님의 {금액:,}원 충전을 거절했습니다.",
                    embed=embed,
                    view=view
                )
                
                # 유저에게 DM
                try:
                    user_embed = discord.Embed(
                        title="❌ 충전 거절",
                        description=f"**{금액:,}원** 충전 신청이 거절되었습니다.",
                        color=0xED4245
                    )
                    user_embed.add_field(name="안내", value="관리자에게 문의하세요.", inline=False)
                    await interaction.user.send(embed=user_embed)
                except Exception as e:
                    print(f"❌ 유저 DM 전송 실패: {e}")
            except Exception as e:
                print(f"❌ 거절 처리 오류: {e}")
                await btn_interaction.response.send_message(f"❌ 오류 발생: {e}", ephemeral=True)
        
        approve_btn.callback = approve_callback
        reject_btn.callback = reject_callback
        view.add_item(approve_btn)
        view.add_item(reject_btn)
        
        # 관리자에게 DM 전송
        try:
            dm_message = await admin_user.send(embed=embed, view=view)
            print(f"✅ 관리자에게 DM 전송 성공 (Message ID: {dm_message.id})")
            await interaction.followup.send(
                f"✅ 충전 신청이 완료되었습니다!\n\n💰 신청 금액: **{금액:,}원**\n📧 관리자 확인 후 처리됩니다.",
                ephemeral=True
            )
        except discord.Forbidden:
            print("❌ 관리자 DM 전송 실패: Forbidden")
            await interaction.followup.send(
                "❌ 관리자에게 메시지를 보낼 수 없습니다.\n\n관리자가 봇의 DM을 차단했거나 DM 설정이 꺼져있습니다.\n관리자에게 다음을 확인하도록 요청하세요:\n1. 개인정보 보호 및 보안 설정\n2. 서버 멤버로부터의 다이렉트 메시지 허용",
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ DM 전송 오류: {e}")
            await interaction.followup.send(
                f"❌ 메시지 전송 중 오류가 발생했습니다.\n오류 내용: {str(e)}\n\n관리자에게 문의하세요.",
                ephemeral=True
            )
    
    except Exception as e:
        print(f"❌ 충전신청 오류: {e}")
        try:
            await interaction.followup.send(f"❌ 오류가 발생했습니다: {e}", ephemeral=True)
        except:
            pass

@bot.tree.command(name="제품추가", description="제품 관리 사이트 링크를 보여줍니다", guild=discord.Object(id=GUILD_ID))
async def add_product_link(interaction: discord.Interaction):
    admin_id = load_admin()
    
    # 관리자 확인
    if not admin_id or interaction.user.id != admin_id:
        await interaction.response.send_message("❌ 이 명령어는 관리자만 사용할 수 있습니다!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🛒 제품 관리 사이트", 
        description="아래 링크에서 제품을 추가/삭제할 수 있습니다.\n\n**[👉 여기를 클릭하여 제품 관리하기](http://127.0.0.1:16121/vending_bot/index.html)**\n\n제품을 추가하면 자동으로 저장됩니다!", 
        color=0x5865F2
    )
    embed.set_footer(text="💡 제품 추가 후 구매 버튼 클릭하면 바로 반영됩니다!")
    
    # 관리자 DM으로 전송
    try:
        await interaction.user.send(embed=embed)
        await interaction.response.send_message("✅ DM으로 제품 관리 링크를 전송했습니다!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ DM을 보낼 수 없습니다. DM 설정을 확인해주세요.\n\n**제품 관리 링크:**\nhttp://127.0.0.1:16121/vending_bot/index.html",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ 오류 발생: {e}", ephemeral=True)

@bot.tree.command(name="생성", description="자판기를 생성합니다", guild=discord.Object(id=GUILD_ID))
async def create_vending(interaction: discord.Interaction):
    embed = discord.Embed(
        title="민준 서비스", 
        description="**민준 서비스 자판기**\n\n• 현재 충전시 10% 추가증정 혜택이고 있습니다.\n• 문제 발생시 문의 주세요 # | • | • 📢 | 문의하기", 
        color=0x2ecc71
    )
    
    view = discord.ui.View(timeout=None)
    
    # 첫 번째 줄 버튼들
    button_public = discord.ui.Button(label="공지", style=discord.ButtonStyle.blurple, emoji="📢", row=0)
    button_product = discord.ui.Button(label="제품", style=discord.ButtonStyle.blurple, emoji="📦", row=0)
    button_info = discord.ui.Button(label="정보", style=discord.ButtonStyle.blurple, emoji="ℹ️", row=0)
    
    # 두 번째 줄 버튼들
    button_charge = discord.ui.Button(label="충전", style=discord.ButtonStyle.secondary, emoji="💳", row=1)
    button_reservation = discord.ui.Button(label="예약", style=discord.ButtonStyle.secondary, emoji="📅", row=1)
    button_purchase = discord.ui.Button(label="구매", style=discord.ButtonStyle.success, emoji="🛒", row=1)
    
    async def public_callback(interaction: discord.Interaction):
        await interaction.response.send_message("📢 공지 버튼 클릭됨", ephemeral=True)
    
    async def product_callback(interaction: discord.Interaction):
        products = load_products()
        if not products:
            await interaction.response.send_message(
                "❌ 등록된 제품이 없습니다.\n\n`/제품추가` 명령어로 제품 관리 사이트에 접속하세요!", 
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📦 제품 카테고리", 
            description=f"총 **{len(products)}개**의 제품이 등록되어 있습니다.", 
            color=0x5865F2
        )
        
        for product in products[:25]:
            embed.add_field(
                name=f"{product['name']}", 
                value=f"💰 가격: {product['price']:,}원\n📦 재고: {product['stock']}개\n{get_star_display(product['rating'])}", 
                inline=True
            )
        
        if len(products) > 25:
            embed.set_footer(text=f"+ {len(products) - 25}개 제품이 더 있습니다")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def info_callback(interaction: discord.Interaction):
        user_info_data = load_user_info()
        user_id = str(interaction.user.id)
        money = get_user_money(interaction.user.id)
        
        if user_id not in user_info_data:
            modal = UserInfoModal()
            await interaction.response.send_modal(modal)
        else:
            info = user_info_data[user_id]
            embed = discord.Embed(title="ℹ️ 내 정보", color=0x5865F2)
            embed.add_field(name="👤 이름", value=info['name'], inline=True)
            embed.add_field(name="💰 잔액", value=f"{money:,}원", inline=True)
            embed.add_field(name="📞 전화번호", value=info['phone'], inline=True)
            
            info_view = discord.ui.View()
            edit_btn = discord.ui.Button(label="정보 수정", style=discord.ButtonStyle.primary, emoji="✏️")
            
            async def edit_callback(btn_interaction: discord.Interaction):
                modal = UserInfoModal()
                modal.name.default = info['name']
                modal.account.default = info['account']
                modal.phone.default = info['phone']
                await btn_interaction.response.send_modal(modal)
            
            edit_btn.callback = edit_callback
            info_view.add_item(edit_btn)
            
            await interaction.response.send_message(embed=embed, view=info_view, ephemeral=True)
    
    async def charge_callback(interaction: discord.Interaction):
        embed = discord.Embed(
            title="💳 충전하기", 
            description="**충전 계좌 정보**\n\n🏦 은행: 토스뱅크\n💳 계좌번호: 1908-8667-3506\n👤 예금주: 이민준\n\n**충전 방법:**\n`/충전신청 [금액] [이미지]` 명령어 사용", 
            color=0x57F287
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def reservation_callback(interaction: discord.Interaction):
        await interaction.response.send_message("📅 예약 버튼 클릭됨", ephemeral=True)
    
    async def purchase_callback(interaction: discord.Interaction):
        products = load_products()
        if not products:
            await interaction.response.send_message(
                "❌ 등록된 제품이 없습니다.\n\n`/제품추가` 명령어로 제품 관리 사이트에 접속하세요!", 
                ephemeral=True
            )
            return
        
        product_view = discord.ui.View(timeout=180)
        options = []
        
        for product in products[:25]:
            options.append(discord.SelectOption(
                label=product['name'], 
                description=f"{product['price']:,}원 | 재고: {product['stock']}개 | {get_star_display(product['rating'])}", 
                value=str(product['id'])
            ))
        
        select = discord.ui.Select(placeholder="구매할 제품을 선택하세요...", options=options)
        
        async def select_callback(select_interaction: discord.Interaction):
            selected_id = int(select_interaction.data['values'][0])
            product = next((p for p in products if p['id'] == selected_id), None)
            
            if not product:
                await select_interaction.response.send_message("❌ 제품을 찾을 수 없습니다.", ephemeral=True)
                return
            
            product_embed = discord.Embed(title=f"📦 {product['name']}", color=0x2ecc71)
            product_embed.add_field(name="💰 가격", value=f"{product['price']:,}원", inline=True)
            product_embed.add_field(name="📦 재고", value=f"{product['stock']}개", inline=True)
            product_embed.add_field(name="⭐ 별점", value=get_star_display(product['rating']), inline=True)
            
            confirm_view = discord.ui.View(timeout=60)
            confirm_btn = discord.ui.Button(label="구매하기", style=discord.ButtonStyle.success, emoji="✅")
            cancel_btn = discord.ui.Button(label="취소", style=discord.ButtonStyle.secondary, emoji="❌")
            
            async def confirm_callback(confirm_interaction: discord.Interaction):
                current_products = load_products()
                current_product = next((p for p in current_products if p['id'] == selected_id), None)
                
                if not current_product or current_product['stock'] <= 0:
                    await confirm_interaction.response.send_message("❌ 재고가 부족합니다!", ephemeral=True)
                    return
                
                if not subtract_user_money(confirm_interaction.user.id, product['price']):
                    money = get_user_money(confirm_interaction.user.id)
                    await confirm_interaction.response.send_message(
                        f"❌ 잔액이 부족합니다!\n현재 잔액: {money:,}원\n필요 금액: {product['price']:,}원", 
                        ephemeral=True
                    )
                    return
                
                for p in current_products:
                    if p['id'] == selected_id:
                        p['stock'] -= 1
                        break
                
                save_products_file(current_products)
                new_balance = get_user_money(confirm_interaction.user.id)
                
                # 구매 완료 메시지
                await confirm_interaction.response.send_message(
                    f"✅ **{product['name']}** 구매가 완료되었습니다!\n💰 결제 금액: **{product['price']:,}원**\n💵 남은 잔액: **{new_balance:,}원**", 
                    ephemeral=True
                )
                
                # 구매자에게 DM 전송
                try:
                    dm_embed = discord.Embed(
                        title="🎉 제품 구매 감사합니다!",
                        description=f"**{product['name']}** 구매가 완료되었습니다!",
                        color=0x57F287
                    )
                    dm_embed.add_field(name="💰 결제 금액", value=f"{product['price']:,}원", inline=True)
                    dm_embed.add_field(name="💵 남은 잔액", value=f"{new_balance:,}원", inline=True)
                    dm_embed.set_footer(text="아래 버튼을 눌러 후기를 남겨주세요!")
                    
                    review_view = discord.ui.View(timeout=None)
                    review_btn = discord.ui.Button(label="후기 남기기", style=discord.ButtonStyle.primary, emoji="✍️")
                    
                    async def review_callback(review_interaction: discord.Interaction):
                        modal = ReviewModal(product['name'], review_interaction.user.id, confirm_interaction.guild.id)
                        await review_interaction.response.send_modal(modal)
                    
                    review_btn.callback = review_callback
                    review_view.add_item(review_btn)
                    
                    await confirm_interaction.user.send(embed=dm_embed, view=review_view)
                    print(f"✅ {confirm_interaction.user}님에게 구매 완료 DM 전송")
                except discord.Forbidden:
                    print(f"⚠️ {confirm_interaction.user}님에게 DM 전송 실패 (DM 차단)")
                except Exception as e:
                    print(f"❌ DM 전송 오류: {e}")
                
                # 구매자 역할 부여 (구매 시점에는 부여하지 않고 후기 작성 시에만 부여)
                # settings = load_settings()
                # buyer_role_id = settings.get("buyer_role_id")
                
                # if buyer_role_id:
                #     try:
                #         guild = confirm_interaction.guild
                #         member = guild.get_member(confirm_interaction.user.id)
                #         role = guild.get_role(buyer_role_id)
                #         
                #         if role and member and role not in member.roles:
                #             await member.add_roles(role)
                #             print(f"✅ {member}님에게 구매자 역할 부여")
                #     except Exception as e:
                #         print(f"❌ 역할 부여 오류: {e}")
            
            async def cancel_callback(cancel_interaction: discord.Interaction):
                await cancel_interaction.response.send_message("❌ 구매를 취소했습니다.", ephemeral=True)
            
            confirm_btn.callback = confirm_callback
            cancel_btn.callback = cancel_callback
            confirm_view.add_item(confirm_btn)
            confirm_view.add_item(cancel_btn)
            
            await select_interaction.response.send_message(embed=product_embed, view=confirm_view, ephemeral=True)
        
        select.callback = select_callback
        product_view.add_item(select)
        
        purchase_embed = discord.Embed(
            title="🛒 제품 구매", 
            description="구매할 제품을 선택해주세요:", 
            color=0x57F287
        )
        await interaction.response.send_message(embed=purchase_embed, view=product_view, ephemeral=True)
    
    # 콜백 연결
    button_public.callback = public_callback
    button_product.callback = product_callback
    button_info.callback = info_callback
    button_charge.callback = charge_callback
    button_reservation.callback = reservation_callback
    button_purchase.callback = purchase_callback
    
    # custom_id 설정
    button_public.custom_id = "공지"
    button_product.custom_id = "제품"
    button_info.custom_id = "정보"
    button_charge.custom_id = "충전"
    button_reservation.custom_id = "예약"
    button_purchase.custom_id = "구매"
    
    # 버튼 추가
    view.add_item(button_public)
    view.add_item(button_product)
    view.add_item(button_info)
    view.add_item(button_charge)
    view.add_item(button_reservation)
    view.add_item(button_purchase)
    
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ 자판기 생성 완료", ephemeral=True)

async def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())