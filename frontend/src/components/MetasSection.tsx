
import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/hooks/use-toast';
import { Target, TrendingUp, BarChart3, Plus, Edit, Trash2, Calendar, User, Users as UsersIcon, Trophy, Activity } from 'lucide-react';
import { SectionHeader } from '@/components/shared/SectionHeader';
import { goalAPI, userAPI, ticketAPI } from '@/services/api';

interface Goal {
  id: string;
  title: string;
  description?: string;
  target_value: number;
  current_value: number;
  unit: string;
  user_id?: string;
  team_id?: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  department?: string;
}

interface PerformanceMetrics {
  totalTickets: number;
  resolvedTickets: number;
  averageResolutionTime: number;
  satisfactionRating: number;
}

const MetasSection = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [selectedUser, setSelectedUser] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    target_value: 0,
    unit: 'tickets',
    user_id: '',
    team_id: '',
    start_date: '',
    end_date: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadGoals(),
        loadUsers(),
        loadPerformanceMetrics(),
      ]);
    } finally {
      setLoading(false);
    }
  };

  const loadGoals = async () => {
    try {
      const response = await goalAPI.getAll() as any;
      if (response.success) {
        setGoals(response.data);
      }
    } catch (error) {
      console.error('Error loading goals:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await userAPI.getAll() as any;
      if (response.success) {
        setUsers(response.data);
      }
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const loadPerformanceMetrics = async () => {
    try {
      // Calculate performance metrics from tickets
      const ticketsResponse = await ticketAPI.getAll() as any;
      if (ticketsResponse.success) {
        const tickets = ticketsResponse.data;
        const resolvedTickets = tickets.filter((t: any) => t.status === 'resolved');
        const ratedTickets = tickets.filter((t: any) => t.satisfaction_rating);
        
        const avgRating = ratedTickets.length > 0 
          ? ratedTickets.reduce((sum: number, t: any) => sum + t.satisfaction_rating, 0) / ratedTickets.length
          : 0;

        setPerformanceMetrics({
          totalTickets: tickets.length,
          resolvedTickets: resolvedTickets.length,
          averageResolutionTime: 3.2, // Mock value - would need actual calculation
          satisfactionRating: avgRating,
        });
      }
    } catch (error) {
      console.error('Error loading performance metrics:', error);
    }
  };

  const handleCreateGoal = async () => {
    try {
      const goalData = {
        ...formData,
        start_date: new Date(formData.start_date).toISOString(),
        end_date: new Date(formData.end_date).toISOString(),
      };
      
      const response = await goalAPI.create(goalData) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Meta criada com sucesso",
        });
        setIsCreateDialogOpen(false);
        resetForm();
        loadGoals();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao criar meta",
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

  const handleUpdateGoal = async () => {
    if (!editingGoal) return;
    
    try {
      const goalData = {
        ...formData,
        start_date: new Date(formData.start_date).toISOString(),
        end_date: new Date(formData.end_date).toISOString(),
      };
      
      const response = await goalAPI.update(editingGoal.id, goalData) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Meta atualizada com sucesso",
        });
        setEditingGoal(null);
        resetForm();
        loadGoals();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao atualizar meta",
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

  const handleDeleteGoal = async (goalId: string) => {
    if (!confirm('Tem certeza que deseja excluir esta meta?')) return;
    
    try {
      const response = await goalAPI.delete(goalId) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Meta excluída com sucesso",
        });
        loadGoals();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao excluir meta",
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

  const handleUpdateProgress = async (goalId: string, newValue: number) => {
    try {
      const response = await goalAPI.updateProgress(goalId, newValue) as any;
      if (response.success) {
        toast({
          title: "Sucesso",
          description: "Progresso atualizado com sucesso",
        });
        loadGoals();
      } else {
        toast({
          title: "Erro",
          description: response.message || "Erro ao atualizar progresso",
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

  const openEditDialog = (goal: Goal) => {
    setEditingGoal(goal);
    setFormData({
      title: goal.title,
      description: goal.description || '',
      target_value: goal.target_value,
      unit: goal.unit,
      user_id: goal.user_id || '',
      team_id: goal.team_id || '',
      start_date: goal.start_date.split('T')[0],
      end_date: goal.end_date.split('T')[0],
    });
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      target_value: 0,
      unit: 'tickets',
      user_id: '',
      team_id: '',
      start_date: '',
      end_date: '',
    });
  };

  const filteredGoals = goals.filter(goal => {
    if (selectedUser === 'all') return true;
    return goal.user_id === selectedUser;
  });

  const getProgressPercentage = (goal: Goal) => {
    return Math.min((goal.current_value / goal.target_value) * 100, 100);
  };

  const getGoalStatus = (goal: Goal) => {
    const now = new Date();
    const endDate = new Date(goal.end_date);
    const progress = getProgressPercentage(goal);
    
    if (progress >= 100) return { label: 'Concluída', color: 'bg-green-100 text-green-800' };
    if (endDate < now) return { label: 'Expirada', color: 'bg-red-100 text-red-800' };
    if (progress >= 75) return { label: 'Progresso Bom', color: 'bg-blue-100 text-blue-800' };
    if (progress >= 50) return { label: 'No Caminho', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'Iniciando', color: 'bg-gray-100 text-gray-800' };
  };

  const getUserName = (userId: string) => {
    const user = users.find(u => u.id === userId);
    return user ? user.name : 'Usuário não encontrado';
  };

  const getUnitLabel = (unit: string) => {
    const units: { [key: string]: string } = {
      tickets: 'tickets',
      calls: 'ligações',
      satisfaction: 'satisfação',
      hours: 'horas',
      percentage: '%',
    };
    return units[unit] || unit;
  };

  return (
    <div className="p-8">
      <SectionHeader
        title="Metas e Desempenho"
        subtitle="Acompanhamento de produtividade e resultados"
        emoji="🎯"
      />

      <Tabs defaultValue="produtividade" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="produtividade" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Painel de Produtividade
          </TabsTrigger>
          <TabsTrigger value="metas" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Metas por Equipe
          </TabsTrigger>
          <TabsTrigger value="historicos" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Comparativos Históricos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="produtividade" className="mt-6">
          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-primary">
                      {performanceMetrics ? Math.round((performanceMetrics.resolvedTickets / performanceMetrics.totalTickets) * 100) : 0}%
                    </div>
                    <div className="text-sm text-muted-foreground">Taxa de Resolução</div>
                  </div>
                  <Trophy className="h-8 w-8 text-primary" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-emerald-600">
                      {performanceMetrics?.averageResolutionTime.toFixed(1) || 0}min
                    </div>
                    <div className="text-sm text-muted-foreground">Tempo Médio</div>
                  </div>
                  <Activity className="h-8 w-8 text-emerald-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-purple-600">
                      {performanceMetrics?.totalTickets || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Atendimentos Total</div>
                  </div>
                  <BarChart3 className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-orange-600">
                      {performanceMetrics?.satisfactionRating.toFixed(1) || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Satisfação Média</div>
                  </div>
                  <Target className="h-8 w-8 text-orange-600" />
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* User Performance Ranking */}
          <Card>
            <CardHeader>
              <CardTitle>Ranking de Produtividade</CardTitle>
              <CardDescription>Melhores performers da equipe</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {users.slice(0, 5).map((user, i) => (
                  <div key={user.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg font-bold text-gray-400">#{i + 1}</span>
                      <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <div className="font-medium">{user.name}</div>
                        <div className="text-sm text-gray-500">{user.department}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {Math.floor(Math.random() * 20) + 80}% eficiência
                      </div>
                      <div className="text-sm text-gray-500">
                        {Math.floor(Math.random() * 30) + 20} tickets
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metas" className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Metas por Equipe</CardTitle>
                  <CardDescription>Acompanhe o progresso das metas individuais e de equipe</CardDescription>
                </div>
                <div className="flex gap-2">
                  <Select value={selectedUser} onValueChange={setSelectedUser}>
                    <SelectTrigger className="w-48">
                      <SelectValue placeholder="Filtrar por usuário" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos os usuários</SelectItem>
                      {users.map(user => (
                        <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                    <DialogTrigger asChild>
                      <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Nova Meta
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                      <DialogHeader>
                        <DialogTitle>Criar Nova Meta</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="title">Título</Label>
                          <Input
                            id="title"
                            value={formData.title}
                            onChange={(e) => setFormData({...formData, title: e.target.value})}
                            placeholder="Ex: Resolver 50 tickets por semana"
                          />
                        </div>
                        <div>
                          <Label htmlFor="description">Descrição</Label>
                          <Input
                            id="description"
                            value={formData.description}
                            onChange={(e) => setFormData({...formData, description: e.target.value})}
                            placeholder="Descrição detalhada da meta"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="target_value">Valor Alvo</Label>
                            <Input
                              id="target_value"
                              type="number"
                              value={formData.target_value}
                              onChange={(e) => setFormData({...formData, target_value: Number(e.target.value)})}
                              placeholder="50"
                            />
                          </div>
                          <div>
                            <Label htmlFor="unit">Unidade</Label>
                            <Select value={formData.unit} onValueChange={(value) => setFormData({...formData, unit: value})}>
                              <SelectTrigger>
                                <SelectValue placeholder="Unidade" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="tickets">Tickets</SelectItem>
                                <SelectItem value="calls">Ligações</SelectItem>
                                <SelectItem value="satisfaction">Satisfação</SelectItem>
                                <SelectItem value="hours">Horas</SelectItem>
                                <SelectItem value="percentage">Porcentagem</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                        <div>
                          <Label htmlFor="user_id">Usuário</Label>
                          <Select value={formData.user_id} onValueChange={(value) => setFormData({...formData, user_id: value})}>
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione um usuário" />
                            </SelectTrigger>
                            <SelectContent>
                              {users.map(user => (
                                <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="start_date">Data Início</Label>
                            <Input
                              id="start_date"
                              type="date"
                              value={formData.start_date}
                              onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                            />
                          </div>
                          <div>
                            <Label htmlFor="end_date">Data Fim</Label>
                            <Input
                              id="end_date"
                              type="date"
                              value={formData.end_date}
                              onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                            />
                          </div>
                        </div>
                        <Button onClick={handleCreateGoal} className="w-full">
                          Criar Meta
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-muted-foreground">Carregando metas...</div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {filteredGoals.map((goal) => {
                    const progress = getProgressPercentage(goal);
                    const status = getGoalStatus(goal);
                    
                    return (
                      <Card key={goal.id} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h3 className="font-semibold text-lg">{goal.title}</h3>
                              {goal.description && (
                                <p className="text-sm text-muted-foreground">{goal.description}</p>
                              )}
                            </div>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => openEditDialog(goal)}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteGoal(goal.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                          
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <Badge className={status.color}>{status.label}</Badge>
                              <span className="text-sm font-medium">
                                {goal.current_value} / {goal.target_value} {getUnitLabel(goal.unit)}
                              </span>
                            </div>
                            
                            <Progress value={progress} className="h-2" />
                            
                            <div className="flex items-center justify-between text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <User className="h-3 w-3" />
                                {goal.user_id ? getUserName(goal.user_id) : 'Equipe'}
                              </span>
                              <span className="flex items-center gap-1">
                                <Calendar className="h-3 w-3" />
                                {new Date(goal.end_date).toLocaleDateString('pt-BR')}
                              </span>
                            </div>
                            
                            <div className="flex gap-2">
                              <Input
                                type="number"
                                placeholder="Novo valor"
                                className="flex-1"
                                onKeyPress={(e) => {
                                  if (e.key === 'Enter') {
                                    const value = Number((e.target as HTMLInputElement).value);
                                    if (value >= 0) {
                                      handleUpdateProgress(goal.id, value);
                                      (e.target as HTMLInputElement).value = '';
                                    }
                                  }
                                }}
                              />
                              <Button
                                size="sm"
                                onClick={(e) => {
                                  const input = (e.target as HTMLButtonElement).parentElement?.querySelector('input');
                                  if (input) {
                                    const value = Number(input.value);
                                    if (value >= 0) {
                                      handleUpdateProgress(goal.id, value);
                                      input.value = '';
                                    }
                                  }
                                }}
                              >
                                Atualizar
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historicos" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Comparativos Históricos</CardTitle>
              <CardDescription>Evolução da performance ao longo do tempo</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
                <div className="text-center">
                  <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Gráfico de evolução histórica</p>
                  <p className="text-sm text-gray-400">Visualização de tendências e comparações mensais</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit Goal Dialog */}
      <Dialog open={!!editingGoal} onOpenChange={(open) => !open && setEditingGoal(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Meta</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-title">Título</Label>
              <Input
                id="edit-title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="Ex: Resolver 50 tickets por semana"
              />
            </div>
            <div>
              <Label htmlFor="edit-description">Descrição</Label>
              <Input
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Descrição detalhada da meta"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-target_value">Valor Alvo</Label>
                <Input
                  id="edit-target_value"
                  type="number"
                  value={formData.target_value}
                  onChange={(e) => setFormData({...formData, target_value: Number(e.target.value)})}
                  placeholder="50"
                />
              </div>
              <div>
                <Label htmlFor="edit-unit">Unidade</Label>
                <Select value={formData.unit} onValueChange={(value) => setFormData({...formData, unit: value})}>
                  <SelectTrigger>
                    <SelectValue placeholder="Unidade" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tickets">Tickets</SelectItem>
                    <SelectItem value="calls">Ligações</SelectItem>
                    <SelectItem value="satisfaction">Satisfação</SelectItem>
                    <SelectItem value="hours">Horas</SelectItem>
                    <SelectItem value="percentage">Porcentagem</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="edit-user_id">Usuário</Label>
              <Select value={formData.user_id} onValueChange={(value) => setFormData({...formData, user_id: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione um usuário" />
                </SelectTrigger>
                <SelectContent>
                  {users.map(user => (
                    <SelectItem key={user.id} value={user.id}>{user.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-start_date">Data Início</Label>
                <Input
                  id="edit-start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="edit-end_date">Data Fim</Label>
                <Input
                  id="edit-end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                />
              </div>
            </div>
            <Button onClick={handleUpdateGoal} className="w-full">
              Salvar Alterações
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MetasSection;
