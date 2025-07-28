
import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { toast } from '@/hooks/use-toast';
import { Users, UserCheck, Shield, Plus, Edit, Trash2, Search, Mail, Phone, Activity } from 'lucide-react';
import { userAPI } from '@/services/api';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'manager' | 'agent' | 'supervisor';
  status: 'active' | 'inactive' | 'busy' | 'available' | 'break';
  phone?: string;
  department?: string;
  avatar_url?: string;
  skills: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const EquipeSection = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'agent' as const,
    phone: '',
    department: '',
    skills: [] as string[],
  });

  // Load users on component mount
  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await userAPI.getAll() as any;
      if (response.success) {
        setUsers(response.data);
      } else {
        toast({
          title: "Erro",
          description: "Não foi possível carregar a lista de usuários",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      const response = await userAPI.create(formData) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Usuário criado com sucesso",
        });
        setIsCreateDialogOpen(false);
        setFormData({
          name: '',
          email: '',
          role: 'agent',
          phone: '',
          department: '',
          skills: [],
        });
        loadUsers();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao criar usuário",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const handleUpdateUser = async () => {
    if (!editingUser) return;
    
    try {
      const response = await userAPI.update(editingUser.id, formData) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Usuário atualizado com sucesso",
        });
        setEditingUser(null);
        setFormData({
          name: '',
          email: '',
          role: 'agent',
          phone: '',
          department: '',
          skills: [],
        });
        loadUsers();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao atualizar usuário",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;
    
    try {
      const response = await userAPI.delete(userId) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Usuário excluído com sucesso",
        });
        loadUsers();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao excluir usuário",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const handleStatusChange = async (userId: string, newStatus: string) => {
    try {
      const response = await userAPI.updateStatus(userId, newStatus) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Status atualizado com sucesso",
        });
        loadUsers();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao atualizar status",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao conectar com o servidor",
        variant: "destructive",
      });
    }
  };

  const openEditDialog = (user: User) => {
    setEditingUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      role: user.role,
      phone: user.phone || '',
      department: user.department || '',
      skills: user.skills || [],
    });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'all' || user.role === selectedRole;
    const matchesStatus = selectedStatus === 'all' || user.status === selectedStatus;
    return matchesSearch && matchesRole && matchesStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-100 text-green-800 border-green-200';
      case 'busy': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'break': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'inactive': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'available': return 'Disponível';
      case 'busy': return 'Ocupado';
      case 'break': return 'Pausa';
      case 'inactive': return 'Inativo';
      default: return 'Ativo';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return 'Administrador';
      case 'manager': return 'Gerente';
      case 'supervisor': return 'Supervisor';
      case 'agent': return 'Agente';
      default: return role;
    }
  };

  const statusCounts = {
    available: users.filter(u => u.status === 'available').length,
    busy: users.filter(u => u.status === 'busy').length,
    break: users.filter(u => u.status === 'break').length,
    inactive: users.filter(u => u.status === 'inactive').length,
  };

  const roleCounts = {
    admin: users.filter(u => u.role === 'admin').length,
    manager: users.filter(u => u.role === 'manager').length,
    supervisor: users.filter(u => u.role === 'supervisor').length,
    agent: users.filter(u => u.role === 'agent').length,
  };

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-2">
          <Users className="h-8 w-8" />
          Equipe
        </h1>
        <p className="text-muted-foreground">Gestão completa da equipe de atendimento</p>
      </div>

      <Tabs defaultValue="operadores" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="operadores" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Listagem de Operadores
          </TabsTrigger>
          <TabsTrigger value="status" className="flex items-center gap-2">
            <UserCheck className="h-4 w-4" />
            Status Atual
          </TabsTrigger>
          <TabsTrigger value="cargos" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Cargos e Agrupamentos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="operadores" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Listagem de Operadores</CardTitle>
                  <CardDescription>Gerencie os usuários do sistema</CardDescription>
                </div>
                <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Novo Usuário
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Criar Novo Usuário</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="name">Nome</Label>
                        <Input
                          id="name"
                          value={formData.name}
                          onChange={(e) => setFormData({...formData, name: e.target.value})}
                          placeholder="Nome completo"
                        />
                      </div>
                      <div>
                        <Label htmlFor="email">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          value={formData.email}
                          onChange={(e) => setFormData({...formData, email: e.target.value})}
                          placeholder="email@starprint.com"
                        />
                      </div>
                      <div>
                        <Label htmlFor="role">Cargo</Label>
                        <Select value={formData.role} onValueChange={(value: any) => setFormData({...formData, role: value})}>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o cargo" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="agent">Agente</SelectItem>
                            <SelectItem value="supervisor">Supervisor</SelectItem>
                            <SelectItem value="manager">Gerente</SelectItem>
                            <SelectItem value="admin">Administrador</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="phone">Telefone</Label>
                        <Input
                          id="phone"
                          value={formData.phone}
                          onChange={(e) => setFormData({...formData, phone: e.target.value})}
                          placeholder="+55 11 99999-9999"
                        />
                      </div>
                      <div>
                        <Label htmlFor="department">Departamento</Label>
                        <Input
                          id="department"
                          value={formData.department}
                          onChange={(e) => setFormData({...formData, department: e.target.value})}
                          placeholder="Ex: Suporte, Vendas, etc."
                        />
                      </div>
                      <Button onClick={handleCreateUser} className="w-full">
                        Criar Usuário
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex gap-4 mb-6">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar por nome ou email..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={selectedRole} onValueChange={setSelectedRole}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filtrar por cargo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os cargos</SelectItem>
                    <SelectItem value="admin">Administrador</SelectItem>
                    <SelectItem value="manager">Gerente</SelectItem>
                    <SelectItem value="supervisor">Supervisor</SelectItem>
                    <SelectItem value="agent">Agente</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filtrar por status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os status</SelectItem>
                    <SelectItem value="available">Disponível</SelectItem>
                    <SelectItem value="busy">Ocupado</SelectItem>
                    <SelectItem value="break">Pausa</SelectItem>
                    <SelectItem value="inactive">Inativo</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Users Grid */}
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-muted-foreground">Carregando usuários...</div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredUsers.map((user) => (
                    <Card key={user.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                              <Users className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                              <h3 className="font-medium text-foreground">{user.name}</h3>
                              <p className="text-sm text-muted-foreground flex items-center gap-1">
                                <Mail className="h-3 w-3" />
                                {user.email}
                              </p>
                            </div>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openEditDialog(user)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteUser(user.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Badge variant="outline" className={getStatusColor(user.status)}>
                              <Activity className="h-3 w-3 mr-1" />
                              {getStatusLabel(user.status)}
                            </Badge>
                            <Badge variant="secondary">
                              {getRoleLabel(user.role)}
                            </Badge>
                          </div>
                          
                          {user.phone && (
                            <p className="text-sm text-muted-foreground flex items-center gap-1">
                              <Phone className="h-3 w-3" />
                              {user.phone}
                            </p>
                          )}
                          
                          {user.department && (
                            <p className="text-sm text-muted-foreground">
                              {user.department}
                            </p>
                          )}
                          
                          <div className="flex gap-2 mt-2">
                            <Select
                              value={user.status}
                              onValueChange={(value) => handleStatusChange(user.id, value)}
                            >
                              <SelectTrigger className="h-8">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="available">Disponível</SelectItem>
                                <SelectItem value="busy">Ocupado</SelectItem>
                                <SelectItem value="break">Pausa</SelectItem>
                                <SelectItem value="inactive">Inativo</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="status" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Status Atual da Equipe</CardTitle>
              <CardDescription>Visão geral do status dos membros da equipe</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                  <div className="text-2xl font-bold text-emerald-700">{statusCounts.available}</div>
                  <div className="text-sm text-emerald-600">Disponível</div>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-2xl font-bold text-yellow-700">{statusCounts.busy}</div>
                  <div className="text-sm text-yellow-600">Ocupado</div>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <div className="text-2xl font-bold text-orange-700">{statusCounts.break}</div>
                  <div className="text-sm text-orange-600">Pausa</div>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="text-2xl font-bold text-red-700">{statusCounts.inactive}</div>
                  <div className="text-sm text-red-600">Inativo</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cargos" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Cargos e Agrupamentos</CardTitle>
              <CardDescription>Distribuição da equipe por cargo</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { cargo: 'Administrador', count: roleCounts.admin, cor: 'purple' },
                  { cargo: 'Gerente', count: roleCounts.manager, cor: 'blue' },
                  { cargo: 'Supervisor', count: roleCounts.supervisor, cor: 'green' },
                  { cargo: 'Agente', count: roleCounts.agent, cor: 'yellow' }
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 rounded bg-${item.cor}-500`}></div>
                      <span className="font-medium">{item.cargo}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{item.count} pessoas</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit User Dialog */}
      <Dialog open={!!editingUser} onOpenChange={(open) => !open && setEditingUser(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Editar Usuário</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-name">Nome</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="Nome completo"
              />
            </div>
            <div>
              <Label htmlFor="edit-email">Email</Label>
              <Input
                id="edit-email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                placeholder="email@starprint.com"
              />
            </div>
            <div>
              <Label htmlFor="edit-role">Cargo</Label>
              <Select value={formData.role} onValueChange={(value: any) => setFormData({...formData, role: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o cargo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="agent">Agente</SelectItem>
                  <SelectItem value="supervisor">Supervisor</SelectItem>
                  <SelectItem value="manager">Gerente</SelectItem>
                  <SelectItem value="admin">Administrador</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit-phone">Telefone</Label>
              <Input
                id="edit-phone"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                placeholder="+55 11 99999-9999"
              />
            </div>
            <div>
              <Label htmlFor="edit-department">Departamento</Label>
              <Input
                id="edit-department"
                value={formData.department}
                onChange={(e) => setFormData({...formData, department: e.target.value})}
                placeholder="Ex: Suporte, Vendas, etc."
              />
            </div>
            <Button onClick={handleUpdateUser} className="w-full">
              Salvar Alterações
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EquipeSection;
