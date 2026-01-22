import discord
from utils.data_manager import load_json, save_json

class VendingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected = None

        products = load_json("products.json")
        options = [
            discord.SelectOption(
                label=p["name"],
                description=f"{p['price']}원",
                value=key
            )
            for key, p in products.items()
        ]

        self.select = discord.ui.Select(
            placeholder="상품 선택",
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        self.selected = self.select.values[0]
        await interaction.response.send_message(
            f"선택됨: {self.selected}", ephemeral=True
        )

    @discord.ui.button(label="구매하기", style=discord.ButtonStyle.green)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected:
            return await interaction.response.send_message(
                "상품부터 선택하세요.", ephemeral=True
            )

        users = load_json("users.json")
        products = load_json("products.json")

        uid = str(interaction.user.id)
        users.setdefault(uid, {"balance": 0})

        product = products[self.selected]

        if users[uid]["balance"] < product["price"]:
            return await interaction.response.send_message(
                "잔액 부족", ephemeral=True
            )

        users[uid]["balance"] -= product["price"]
        save_json("users.json", users)

        if product["type"] == "role":
            role = interaction.guild.get_role(product["value"])
            await interaction.user.add_roles(role)

        if product["type"] == "text":
            await interaction.user.send(product["value"])

        await interaction.response.send_message(
            f"{product['name']} 구매 완료!", ephemeral=True
        )
